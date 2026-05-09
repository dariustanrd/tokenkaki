"""HTTP client for external OpenAI-compatible vLLM backends."""

from __future__ import annotations

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


async def forward_chat_completion(
    route: ModelRoute,
    body: dict[str, Any],
    request_id: str,
    timeout_seconds: float = 60.0,
    transport: httpx.AsyncBaseTransport | None = None,
) -> BackendResponse:
    """Forward a non-streaming OpenAI chat completion body to vLLM."""
    forwarded_body = dict(body)
    forwarded_body["model"] = route.backend_model
    url = f"{route.backend_base_url.rstrip('/')}/v1/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds, transport=transport) as client:
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
