"""HTTP client for external OpenAI-compatible vLLM backends."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import httpx

from tokenkaki.registry import ModelRoute


class BackendTimeout(Exception):
    """Raised when a backend request times out."""


class BackendConnectionFailure(Exception):
    """Raised when the gateway cannot reach the backend."""


@dataclass(frozen=True)
class BackendResponse:
    status_code: int
    content: bytes
    media_type: str | None


@dataclass(frozen=True)
class BackendStreamResponse:
    status_code: int
    media_type: str | None
    chunks: AsyncIterator[bytes]


async def forward_chat_completion(
    route: ModelRoute,
    body: dict[str, Any],
    request_id: str,
    timeout_seconds: float = 60.0,
    transport: httpx.AsyncBaseTransport | None = None,
    client: httpx.AsyncClient | None = None,
) -> BackendResponse:
    """Forward a non-streaming OpenAI chat completion body to vLLM."""
    forwarded_body = dict(body)
    forwarded_body["model"] = route.backend_model
    url = f"{route.backend_base_url.rstrip('/')}/v1/chat/completions"

    try:
        if client is None:
            async with httpx.AsyncClient(timeout=timeout_seconds, transport=transport) as request_client:
                response = await request_client.post(
                    url,
                    json=forwarded_body,
                    headers={"x-request-id": request_id},
                )
        else:
            response = await client.post(
                url,
                json=forwarded_body,
                headers={"x-request-id": request_id},
            )
    except httpx.TimeoutException as exc:
        raise BackendTimeout() from exc
    except httpx.RequestError as exc:
        raise BackendConnectionFailure() from exc

    return BackendResponse(
        status_code=response.status_code,
        content=response.content,
        media_type=response.headers.get("content-type"),
    )


@asynccontextmanager
async def open_chat_completion_stream(
    route: ModelRoute,
    body: dict[str, Any],
    request_id: str,
    timeout_seconds: float = 60.0,
    transport: httpx.AsyncBaseTransport | None = None,
    client: httpx.AsyncClient | None = None,
) -> AsyncIterator[BackendStreamResponse]:
    """Open a streaming OpenAI chat completion request to vLLM."""
    forwarded_body = dict(body)
    forwarded_body["model"] = route.backend_model
    url = f"{route.backend_base_url.rstrip('/')}/v1/chat/completions"

    owns_client = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=timeout_seconds, transport=transport)

    try:
        try:
            stream_context = client.stream(
                "POST",
                url,
                json=forwarded_body,
                headers={"x-request-id": request_id},
            )
            response = await stream_context.__aenter__()
        except httpx.TimeoutException as exc:
            raise BackendTimeout() from exc
        except httpx.RequestError as exc:
            raise BackendConnectionFailure() from exc

        try:
            yield BackendStreamResponse(
                status_code=response.status_code,
                media_type=response.headers.get("content-type"),
                chunks=response.aiter_bytes(),
            )
        finally:
            await stream_context.__aexit__(None, None, None)
    finally:
        if owns_client:
            await client.aclose()
