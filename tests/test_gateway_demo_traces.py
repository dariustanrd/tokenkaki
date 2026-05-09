import importlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi.testclient import TestClient

from tokenkaki.backend import BackendResponse, BackendStreamResponse
from tokenkaki.gateway import create_app
from tokenkaki.registry import ModelRoute

gateway_app_module = importlib.import_module("tokenkaki.gateway.app")


def test_demo_run_trace_is_created_for_non_streaming_chat(monkeypatch) -> None:
    async def fake_forward_chat_completion(
        route: ModelRoute,
        body: dict[str, Any],
        request_id: str,
    ) -> BackendResponse:
        return BackendResponse(
            status_code=200,
            content=b'{"id":"chatcmpl-test","object":"chat.completion"}',
            media_type="application/json",
        )

    monkeypatch.setattr(gateway_app_module, "forward_chat_completion", fake_forward_chat_completion)
    client = TestClient(create_app())

    response = client.post(
        "/v1/chat/completions",
        headers={
            "x-request-id": "req-demo-123",
            "x-tokenkaki-session-id": "session-1",
            "x-tokenkaki-user-id": "user-7",
        },
        json={"model": "qwen3-8b", "messages": [{"role": "user", "content": "hi"}]},
    )
    trace_response = client.get("/demo/runs/req-demo-123")

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-demo-123"
    assert trace_response.status_code == 200
    trace = trace_response.json()
    assert trace["request_id"] == "req-demo-123"
    assert trace["session_id"] == "session-1"
    assert trace["user_id"] == "user-7"
    assert trace["model"] == "qwen3-8b"
    assert trace["backend_model"] == "Qwen/Qwen3-8B"
    assert trace["selected_backend"] == "http://127.0.0.1:8001"
    assert trace["routing_policy"] == "static_single_backend"
    assert trace["stream"] is False
    assert trace["status"] == "completed"
    assert trace["status_code"] == 200
    assert trace["error_class"] is None
    assert trace["active_requests_at_start"] == 1
    assert trace["timings_ms"]["total"] is not None
    assert trace["timings_ms"]["first_chunk"] is None


def test_demo_run_trace_records_stream_first_chunk(monkeypatch) -> None:
    async def chunks() -> AsyncIterator[bytes]:
        yield b'data: {"choices":[{"delta":{"content":"hi"}}]}\n\n'
        yield b"data: [DONE]\n\n"

    @asynccontextmanager
    async def fake_open_chat_completion_stream(
        route: ModelRoute,
        body: dict[str, Any],
        request_id: str,
    ) -> AsyncIterator[BackendStreamResponse]:
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
        headers={"x-request-id": "req-demo-stream-123"},
        json={
            "model": "qwen3-8b",
            "stream": True,
            "messages": [{"role": "user", "content": "hi"}],
        },
    ) as response:
        body = response.read()
    trace_response = client.get("/demo/runs/req-demo-stream-123")

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-demo-stream-123"
    assert body.endswith(b"data: [DONE]\n\n")
    assert trace_response.status_code == 200
    trace = trace_response.json()
    assert trace["stream"] is True
    assert trace["status"] == "completed"
    assert trace["status_code"] == 200
    assert trace["streamed_chunk_count"] == 2
    assert trace["timings_ms"]["first_chunk"] is not None
    assert trace["timings_ms"]["total"] is not None


def test_demo_run_station_views_are_generated_from_same_trace(monkeypatch) -> None:
    async def chunks() -> AsyncIterator[bytes]:
        yield b'data: {"choices":[{"delta":{"content":"hi"}}]}\n\n'
        yield b"data: [DONE]\n\n"

    @asynccontextmanager
    async def fake_open_chat_completion_stream(
        route: ModelRoute,
        body: dict[str, Any],
        request_id: str,
    ) -> AsyncIterator[BackendStreamResponse]:
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
        headers={
            "x-request-id": "req-stations-123",
            "x-tokenkaki-session-id": "session-stations",
            "x-tokenkaki-user-id": "user-stations",
        },
        json={
            "model": "qwen3-8b",
            "stream": True,
            "messages": [{"role": "user", "content": "hi"}],
        },
    ) as response:
        response.read()

    assert response.status_code == 200

    gateway = client.get("/demo/runs/req-stations-123/stations/gateway").json()
    queue = client.get("/demo/runs/req-stations-123/stations/queue").json()
    prefill = client.get("/demo/runs/req-stations-123/stations/prefill").json()
    decode = client.get("/demo/runs/req-stations-123/stations/decode").json()
    metrics = client.get("/demo/runs/req-stations-123/stations/metrics").json()

    assert gateway["request_id"] == "req-stations-123"
    assert gateway["station"] == "gateway"
    assert gateway["measurement_basis"] == "measured"
    assert gateway["facts"]["session_id"] == "session-stations"
    assert gateway["facts"]["selected_backend"] == "http://127.0.0.1:8001"
    assert queue["station"] == "queue"
    assert queue["measurement_basis"] == "gateway_observed"
    assert queue["facts"]["active_requests_at_start"] == 1
    assert prefill["station"] == "prefill"
    assert prefill["measurement_basis"] == "gateway_inferred"
    assert prefill["facts"]["first_chunk_ms"] is not None
    assert decode["station"] == "decode"
    assert decode["facts"]["streamed_chunk_count"] == 2
    assert metrics["station"] == "metrics"
    assert metrics["facts"]["status"] == "completed"
    assert metrics["facts"]["status_code"] == 200


def test_demo_run_station_rejects_unknown_station(monkeypatch) -> None:
    async def fake_forward_chat_completion(
        route: ModelRoute,
        body: dict[str, Any],
        request_id: str,
    ) -> BackendResponse:
        return BackendResponse(
            status_code=200,
            content=b'{"id":"chatcmpl-test","object":"chat.completion"}',
            media_type="application/json",
        )

    monkeypatch.setattr(gateway_app_module, "forward_chat_completion", fake_forward_chat_completion)
    client = TestClient(create_app())

    chat_response = client.post(
        "/v1/chat/completions",
        headers={"x-request-id": "req-unknown-station"},
        json={"model": "qwen3-8b", "messages": [{"role": "user", "content": "hi"}]},
    )
    station_response = client.get("/demo/runs/req-unknown-station/stations/router")

    assert chat_response.status_code == 200
    assert station_response.status_code == 404
    assert station_response.json()["error"]["message"] == "unknown station: router"


def test_demo_run_trace_404s_for_unknown_run() -> None:
    client = TestClient(create_app())

    response = client.get("/demo/runs/missing-run")

    assert response.status_code == 404
    assert response.json()["error"]["type"] == "not_found_error"
