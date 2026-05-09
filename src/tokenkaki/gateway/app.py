"""FastAPI gateway application."""

from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack
import logging
import os
import time
from typing import Any
from uuid import uuid4

import httpx
from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import StreamingResponse

from tokenkaki.backend import (
    BackendConnectionFailure,
    BackendTimeout,
    forward_chat_completion,
    open_chat_completion_stream,
)
from tokenkaki.config import load_config
from tokenkaki.registry import ModelRoute, list_public_models, resolve_model

LOGGER = logging.getLogger("tokenkaki.gateway")

REQUEST_COUNT = Counter(
    "tokenkaki_gateway_requests_total",
    "Gateway-observed HTTP requests.",
    ("method", "path", "status"),
)
REQUEST_LATENCY_SECONDS = Histogram(
    "tokenkaki_gateway_request_latency_seconds",
    "Gateway-observed HTTP request latency in seconds.",
    ("method", "path"),
)


def create_app(config_path: str | None = None) -> FastAPI:
    """Create the Milestone 1 gateway application."""
    app = FastAPI(title="tokenkaki gateway", version="0.1.0")
    app.state.config = load_config(config_path or os.getenv("TOKENKAKI_CONFIG"))

    @app.middleware("http")
    async def observe_requests(request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        status = "500"

        try:
            response = await call_next(request)
            status = str(response.status_code)
            return response
        except Exception:
            LOGGER.exception(
                "gateway_request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "error_class": "unexpected_gateway_error",
                },
            )
            raise
        finally:
            duration = time.perf_counter() - start
            path = request.scope.get("route").path if request.scope.get("route") else request.url.path
            REQUEST_COUNT.labels(request.method, path, status).inc()
            REQUEST_LATENCY_SECONDS.labels(request.method, path).observe(duration)

    @app.get("/healthz")
    async def healthz(request: Request) -> dict[str, str]:
        return {"status": "ok", "request_id": request.state.request_id}

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/v1/models")
    async def models() -> dict[str, object]:
        return {"object": "list", "data": list_public_models(app.state.config)}

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request) -> Response:
        body = await request.json()
        if not isinstance(body, dict):
            return _error_response("invalid_request_error", "request body must be a JSON object", 400)

        model = body.get("model")
        if not isinstance(model, str) or not model:
            return _error_response("invalid_request_error", "request body must include a model", 400)

        route = resolve_model(app.state.config, model)
        if route is None:
            return _error_response("invalid_request_error", f"unknown or disabled model: {model}", 404)

        if body.get("stream") is True:
            return await _stream_chat_completion(request, route, body)

        try:
            backend_response = await forward_chat_completion(
                route,
                body,
                request_id=request.state.request_id,
            )
        except BackendTimeout:
            LOGGER.warning(
                "backend_request_timeout",
                extra={
                    "request_id": request.state.request_id,
                    "selected_backend": route.backend_base_url,
                    "error_class": "backend_timeout",
                    "timeout_class": "backend_request_timeout",
                },
            )
            return _error_response("server_error", "backend request timed out", 504)
        except BackendConnectionFailure:
            LOGGER.warning(
                "backend_connection_failed",
                extra={
                    "request_id": request.state.request_id,
                    "selected_backend": route.backend_base_url,
                    "error_class": "backend_connection_failure",
                },
            )
            return _error_response("server_error", "backend connection failed", 502)

        return Response(
            content=backend_response.content,
            status_code=backend_response.status_code,
            media_type=backend_response.media_type,
        )

    return app


app = create_app()


async def _stream_chat_completion(request: Request, route: ModelRoute, body: dict[str, Any]) -> Response:
    stream_started_at = time.perf_counter()
    exit_stack = AsyncExitStack()

    try:
        backend_stream = await exit_stack.enter_async_context(
            open_chat_completion_stream(
                route,
                body,
                request_id=request.state.request_id,
            )
        )
    except BackendTimeout:
        LOGGER.warning(
            "backend_stream_timeout_before_headers",
            extra={
                "request_id": request.state.request_id,
                "selected_backend": route.backend_base_url,
                "status": 504,
                "error_class": "backend_timeout",
                "timeout_class": "backend_stream_open_timeout",
            },
        )
        await exit_stack.aclose()
        return _error_response("server_error", "backend stream timed out", 504)
    except BackendConnectionFailure:
        LOGGER.warning(
            "backend_stream_connection_failed_before_headers",
            extra={
                "request_id": request.state.request_id,
                "selected_backend": route.backend_base_url,
                "status": 502,
                "error_class": "backend_connection_failure",
            },
        )
        await exit_stack.aclose()
        return _error_response("server_error", "backend stream connection failed", 502)

    LOGGER.info(
        "backend_stream_started",
        extra={
            "request_id": request.state.request_id,
            "selected_backend": route.backend_base_url,
            "status": backend_stream.status_code,
            "routing_policy": route.routing_policy,
        },
    )

    async def stream_body():
        status = "completed"
        error_class = None
        try:
            async for chunk in backend_stream.chunks:
                yield chunk
        except asyncio.CancelledError:
            status = "client_disconnected"
            error_class = "client_disconnect"
            raise
        except httpx.TimeoutException:
            status = "backend_timeout"
            error_class = "backend_timeout"
            LOGGER.warning(
                "backend_stream_timeout_after_headers",
                extra={
                    "request_id": request.state.request_id,
                    "selected_backend": route.backend_base_url,
                    "status": backend_stream.status_code,
                    "error_class": error_class,
                    "timeout_class": "backend_stream_read_timeout",
                },
            )
            raise
        except httpx.RequestError:
            status = "backend_connection_failure"
            error_class = "backend_connection_failure"
            LOGGER.warning(
                "backend_stream_connection_failed_after_headers",
                extra={
                    "request_id": request.state.request_id,
                    "selected_backend": route.backend_base_url,
                    "status": backend_stream.status_code,
                    "error_class": error_class,
                },
            )
            raise
        finally:
            duration = time.perf_counter() - stream_started_at
            LOGGER.info(
                "backend_stream_finished",
                extra={
                    "request_id": request.state.request_id,
                    "selected_backend": route.backend_base_url,
                    "status": backend_stream.status_code,
                    "stream_status": status,
                    "error_class": error_class,
                    "duration_seconds": duration,
                },
            )
            await exit_stack.aclose()

    return StreamingResponse(
        stream_body(),
        status_code=backend_stream.status_code,
        media_type=backend_stream.media_type or "text/event-stream",
    )


def _error_response(error_type: str, message: str, status_code: int) -> Response:
    return Response(
        content=_json_error(error_type, message),
        status_code=status_code,
        media_type="application/json",
    )


def _json_error(error_type: str, message: str) -> bytes:
    import json

    return json.dumps(
        {
            "error": {
                "message": message,
                "type": error_type,
                "code": None,
            }
        }
    ).encode("utf-8")
