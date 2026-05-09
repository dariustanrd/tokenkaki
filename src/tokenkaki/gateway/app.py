"""FastAPI gateway application."""

from __future__ import annotations

import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

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


def create_app() -> FastAPI:
    """Create the Milestone 1 gateway application."""
    app = FastAPI(title="tokenkaki gateway", version="0.1.0")

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

    return app


app = create_app()
