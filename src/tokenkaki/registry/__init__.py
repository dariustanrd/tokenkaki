"""Static model registry facade."""

from tokenkaki.registry.static import (
    ModelRoute,
    list_public_models,
    resolve_model,
)

__all__ = ["ModelRoute", "list_public_models", "resolve_model"]
