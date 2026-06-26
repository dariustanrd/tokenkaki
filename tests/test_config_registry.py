from pathlib import Path

import pytest

from tokenkaki.config import load_config
from tokenkaki.registry import list_public_models, resolve_model


def test_load_config_reads_model_registry(tmp_path: Path) -> None:
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

    config = load_config(config_path)

    assert config.models[0].name == "qwen3-0.6b"
    assert config.models[0].backend.type == "vllm"
    assert config.models[0].backend.base_url == "http://gpu-box:8001"
    assert config.models[0].backend.model == "Qwen/Qwen3-0.6B"


def test_registry_lists_enabled_public_aliases_only(tmp_path: Path) -> None:
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

    config = load_config(config_path)

    assert list_public_models(config) == [
        {
            "id": "qwen3-0.6b",
            "object": "model",
            "created": 0,
            "owned_by": "tokenkaki",
        }
    ]


def test_registry_resolves_enabled_alias_to_backend_route() -> None:
    config = load_config()

    route = resolve_model(config, "qwen3-8b")

    assert route is not None
    assert route.public_model == "qwen3-8b"
    assert route.backend_type == "vllm"
    assert route.backend_base_url == "http://127.0.0.1:8001"
    assert route.backend_model == "Qwen/Qwen3-8B"
    assert route.routing_policy == "static_single_backend"


def test_registry_does_not_resolve_unknown_model() -> None:
    assert resolve_model(load_config(), "unknown-model") is None


def test_config_rejects_non_vllm_backend(tmp_path: Path) -> None:
    config_path = tmp_path / "gateway.yaml"
    config_path.write_text(
        """
models:
  - name: qwen3-0.6b
    enabled: true
    backend:
      type: mock
      base_url: http://gpu-box:8001
""",
    )

    with pytest.raises(ValueError, match="backend type must be vllm"):
        load_config(config_path)
