import importlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from tokenkaki.backend import (
    BackendConnectionFailure,
    BackendResponse,
    BackendStreamResponse,
    BackendTimeout,
)
from tokenkaki.gateway import create_app
from tokenkaki.registry import ModelRoute

gateway_app_module = importlib.import_module("tokenkaki.gateway.app")


def test_chat_completion_forwards_non_streaming_request(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "gateway.yaml"
    config_path.write_text(
        """
models:
  - name: qwen3-0.6b
    enabled: true
    backend:
      type: vllm
      base_url: http://gpu-box:8001
      model: Qwen/Qwen3-0.6B
""",
    )
    captured: dict[str, Any] = {}

    async def fake_forward_chat_completion(
        route: ModelRoute,
        body: dict[str, Any],
        request_id: str,
    ) -> BackendResponse:
        captured["route"] = route
        captured["body"] = body
        captured["request_id"] = request_id
        return BackendResponse(
            status_code=200,
            content=b'{"id":"chatcmpl-test","object":"chat.completion"}',
            media_type="application/json",
        )

    monkeypatch.setattr(gateway_app_module, "forward_chat_completion", fake_forward_chat_completion)
    client = TestClient(create_app(config_path=str(config_path)))

    response = client.post(
        "/v1/chat/completions",
        headers={"x-request-id": "req-chat-123"},
        json={
            "model": "qwen3-0.6b",
            "messages": [{"role": "user", "content": "Say hi"}],
            "temperature": 0,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"id": "chatcmpl-test", "object": "chat.completion"}
    assert captured["route"].backend_base_url == "http://gpu-box:8001"
    assert captured["route"].backend_model == "Qwen/Qwen3-0.6B"
    assert captured["body"] == {
        "model": "qwen3-0.6b",
        "messages": [{"role": "user", "content": "Say hi"}],
        "temperature": 0,
    }
    assert captured["request_id"] == "req-chat-123"


def test_chat_completion_rejects_unknown_model() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/chat/completions",
        json={"model": "missing-model", "messages": [{"role": "user", "content": "hi"}]},
    )

    assert response.status_code == 404
    assert response.json()["error"]["type"] == "invalid_request_error"


def test_chat_completion_streams_backend_sse(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    async def chunks() -> AsyncIterator[bytes]:
        yield b'data: {"choices":[{"delta":{"reasoning":"thinking"}}]}\n\n'
        yield b'data: {"choices":[{"delta":{"content":"answer"}}]}\n\n'
        yield b"data: [DONE]\n\n"

    @asynccontextmanager
    async def fake_open_chat_completion_stream(
        route: ModelRoute,
        body: dict[str, Any],
        request_id: str,
    ) -> AsyncIterator[BackendStreamResponse]:
        captured["route"] = route
        captured["body"] = body
        captured["request_id"] = request_id
        yield BackendStreamResponse(
            status_code=200,
            media_type="text/event-stream",
            chunks=chunks(),
        )

    monkeypatch.setattr(gateway_app_module, "open_chat_completion_stream", fake_open_chat_completion_stream)
    client = TestClient(create_app())

    with client.stream(
        "POST",
        "/v1/chat/completions",
        headers={"x-request-id": "req-stream-123"},
        json={
            "model": "qwen3-0.6b",
            "stream": True,
            "messages": [{"role": "user", "content": "hi"}],
            "chat_template_kwargs": {"enable_thinking": False},
        },
    ) as response:
        content = response.read()

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert content == (
        b'data: {"choices":[{"delta":{"reasoning":"thinking"}}]}\n\n'
        b'data: {"choices":[{"delta":{"content":"answer"}}]}\n\n'
        b"data: [DONE]\n\n"
    )
    assert captured["route"].backend_model == "Qwen/Qwen3-0.6B"
    assert captured["body"] == {
        "model": "qwen3-0.6b",
        "stream": True,
        "messages": [{"role": "user", "content": "hi"}],
        "chat_template_kwargs": {"enable_thinking": False},
    }
    assert captured["request_id"] == "req-stream-123"


def test_chat_completion_maps_backend_timeout(monkeypatch) -> None:
    async def fake_forward_chat_completion(
        route: ModelRoute,
        body: dict[str, Any],
        request_id: str,
    ) -> BackendResponse:
        raise BackendTimeout()

    monkeypatch.setattr(gateway_app_module, "forward_chat_completion", fake_forward_chat_completion)
    client = TestClient(create_app())

    response = client.post(
        "/v1/chat/completions",
        json={"model": "qwen3-0.6b", "messages": [{"role": "user", "content": "hi"}]},
    )

    assert response.status_code == 504
    assert response.json()["error"]["message"] == "backend request timed out"


def test_chat_completion_maps_backend_connection_failure(monkeypatch) -> None:
    async def fake_forward_chat_completion(
        route: ModelRoute,
        body: dict[str, Any],
        request_id: str,
    ) -> BackendResponse:
        raise BackendConnectionFailure()

    monkeypatch.setattr(gateway_app_module, "forward_chat_completion", fake_forward_chat_completion)
    client = TestClient(create_app())

    response = client.post(
        "/v1/chat/completions",
        json={"model": "qwen3-0.6b", "messages": [{"role": "user", "content": "hi"}]},
    )

    assert response.status_code == 502
    assert response.json()["error"]["message"] == "backend connection failed"
