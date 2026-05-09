"""Load static gateway configuration."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class BackendConfig:
    type: str
    base_url: str
    model: str | None = None


@dataclass(frozen=True)
class ModelConfig:
    name: str
    enabled: bool
    backend: BackendConfig


@dataclass(frozen=True)
class GatewayConfig:
    models: tuple[ModelConfig, ...]


def load_config(path: str | Path | None = None) -> GatewayConfig:
    """Load gateway config from a YAML file or the packaged default."""
    raw = _load_yaml(path)
    models = raw.get("models")
    if not isinstance(models, list):
        raise ValueError("gateway config must contain a models list")

    return GatewayConfig(models=tuple(_parse_model(item) for item in models))


def _load_yaml(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        text = resources.files("tokenkaki.config").joinpath("default.yaml").read_text()
    else:
        text = Path(path).read_text()

    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ValueError("gateway config must be a YAML mapping")
    return loaded


def _parse_model(raw: Any) -> ModelConfig:
    if not isinstance(raw, dict):
        raise ValueError("each model entry must be a mapping")

    name = raw.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError("model entry must include a non-empty name")

    enabled = raw.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError(f"model {name} enabled must be a boolean")

    backend = raw.get("backend")
    if not isinstance(backend, dict):
        raise ValueError(f"model {name} must include a backend mapping")

    backend_type = backend.get("type")
    if backend_type != "vllm":
        raise ValueError(f"model {name} backend type must be vllm")

    base_url = backend.get("base_url")
    if not isinstance(base_url, str) or not base_url:
        raise ValueError(f"model {name} backend base_url must be a non-empty string")

    backend_model = backend.get("model")
    if backend_model is not None and not isinstance(backend_model, str):
        raise ValueError(f"model {name} backend model must be a string when set")

    return ModelConfig(
        name=name,
        enabled=enabled,
        backend=BackendConfig(type=backend_type, base_url=base_url, model=backend_model),
    )
