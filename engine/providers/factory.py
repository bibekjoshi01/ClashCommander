from __future__ import annotations

from typing import Any

from .base import BaseLLMProvider
from .registry import ProviderRegistry


class ProviderFactory:
    @staticmethod
    def create(name: str, model: str, **kwargs: Any) -> BaseLLMProvider:
        provider_cls = ProviderRegistry.get(name)
        return provider_cls(model=model, **kwargs)
