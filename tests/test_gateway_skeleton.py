from fastapi.testclient import TestClient

from tokenkaki.gateway import create_app


def test_healthz_returns_status_and_request_id() -> None:
    client = TestClient(create_app())

    response = client.get("/healthz", headers={"x-request-id": "req-test-123"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "request_id": "req-test-123"}


def test_metrics_exposes_gateway_request_metrics() -> None:
    client = TestClient(create_app())

    client.get("/healthz")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "tokenkaki_gateway_requests_total" in response.text
    assert 'method="GET",path="/healthz",status="200"' in response.text
    assert "tokenkaki_gateway_request_latency_seconds" in response.text
