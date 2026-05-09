"""Static config-backed model registry."""

from __future__ import annotations

from dataclasses import dataclass

from tokenkaki.config import GatewayConfig, ModelConfig

ROUTING_POLICY = "static_single_backend"


@dataclass(frozen=True)
class ModelRoute:
    public_model: str
    backend_type: str
    backend_base_url: str
    backend_model: str
    routing_policy: str = ROUTING_POLICY


def list_public_models(config: GatewayConfig) -> list[dict[str, int | str]]:
    """Return enabled model aliases in OpenAI-compatible list format."""
    return [
        {
            "id": model.name,
            "object": "model",
            "created": 0,
            "owned_by": "tokenkaki",
        }
        for model in config.models
        if model.enabled
    ]


def resolve_model(config: GatewayConfig, model_name: str) -> ModelRoute | None:
    """Resolve an enabled public model alias to a backend route."""
    model = _find_model(config, model_name)
    if model is None or not model.enabled:
        return None

    return ModelRoute(
        public_model=model.name,
        backend_type=model.backend.type,
        backend_base_url=model.backend.base_url,
        backend_model=model.backend.model or model.name,
    )


def _find_model(config: GatewayConfig, model_name: str) -> ModelConfig | None:
    for model in config.models:
        if model.name == model_name:
            return model
    return None
