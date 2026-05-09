import json
from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest

from tokenkaki.backend.vllm import forward_chat_completion
from tokenkaki.backend.vllm import open_chat_completion_stream
from tokenkaki.registry import ModelRoute


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_forward_chat_completion_rewrites_model_and_preserves_body() -> None:
    captured: dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = request.headers
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"id": "chatcmpl-test", "model": "Qwen/Qwen3-0.6B"},
            headers={"content-type": "application/json"},
        )

    route = ModelRoute(
        public_model="qwen3-0.6b",
        backend_type="vllm",
        backend_base_url="http://gpu-box:8001/",
        backend_model="Qwen/Qwen3-0.6B",
    )

    response = await forward_chat_completion(
        route,
        {
            "model": "qwen3-0.6b",
            "messages": [{"role": "user", "content": "Say hi"}],
            "temperature": 0,
        },
        request_id="req-chat-123",
        transport=httpx.MockTransport(handler),
    )

    assert response.status_code == 200
    assert json.loads(response.content) == {"id": "chatcmpl-test", "model": "Qwen/Qwen3-0.6B"}
    assert captured["url"] == "http://gpu-box:8001/v1/chat/completions"
    assert captured["headers"]["x-request-id"] == "req-chat-123"
    assert captured["body"] == {
        "model": "Qwen/Qwen3-0.6B",
        "messages": [{"role": "user", "content": "Say hi"}],
        "temperature": 0,
    }


@pytest.mark.anyio
async def test_open_chat_completion_stream_rewrites_model_and_preserves_sse() -> None:
    captured: dict[str, Any] = {}
    chunks = [
        b'data: {"choices":[{"delta":{"reasoning":"thinking"}}]}\n\n',
        b'data: {"choices":[{"delta":{"content":"answer"}}]}\n\n',
        b"data: [DONE]\n\n",
    ]

    class ChunkStream(httpx.AsyncByteStream):
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for chunk in chunks:
                yield chunk

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = request.headers
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            stream=ChunkStream(),
            headers={"content-type": "text/event-stream"},
        )

    route = ModelRoute(
        public_model="qwen3-0.6b",
        backend_type="vllm",
        backend_base_url="http://gpu-box:8001/",
        backend_model="Qwen/Qwen3-0.6B",
    )

    async with open_chat_completion_stream(
        route,
        {
            "model": "qwen3-0.6b",
            "stream": True,
            "messages": [{"role": "user", "content": "Say hi"}],
            "chat_template_kwargs": {"enable_thinking": False},
        },
        request_id="req-stream-123",
        transport=httpx.MockTransport(handler),
    ) as response:
        body = b"".join([chunk async for chunk in response.chunks])

    assert response.status_code == 200
    assert response.media_type == "text/event-stream"
    assert body == b"".join(chunks)
    assert captured["url"] == "http://gpu-box:8001/v1/chat/completions"
    assert captured["headers"]["x-request-id"] == "req-stream-123"
    assert captured["body"] == {
        "model": "Qwen/Qwen3-0.6B",
        "stream": True,
        "messages": [{"role": "user", "content": "Say hi"}],
        "chat_template_kwargs": {"enable_thinking": False},
    }
