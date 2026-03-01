from __future__ import annotations

from typing import Dict, List, Type

from .base import BaseLLMProvider


class ProviderRegistry:
    _registry: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: Type[BaseLLMProvider]) -> None:
        if name in cls._registry:
            raise ValueError(f"Provider '{name}' is already registered")
        cls._registry[name] = provider_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseLLMProvider]:
        provider_cls = cls._registry.get(name)
        if not provider_cls:
            raise ValueError(
                f"Provider '{name}' not found. Available: {list(cls._registry.keys())}"
            )
        return provider_cls

    @classmethod
    def list_providers(cls) -> List[str]:
        return list(cls._registry.keys())
