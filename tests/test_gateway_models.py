from pathlib import Path

from fastapi.testclient import TestClient

from tokenkaki.gateway import create_app


def test_models_endpoint_returns_enabled_public_aliases(tmp_path: Path) -> None:
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
  - name: disabled-model
    enabled: false
    backend:
      type: vllm
      base_url: http://gpu-box:8001
""",
    )
    client = TestClient(create_app(config_path=str(config_path)))

    response = client.get("/v1/models")

    assert response.status_code == 200
    assert response.json() == {
        "object": "list",
        "data": [
            {
                "id": "qwen3-0.6b",
                "object": "model",
                "created": 0,
                "owned_by": "tokenkaki",
            }
        ],
    }
