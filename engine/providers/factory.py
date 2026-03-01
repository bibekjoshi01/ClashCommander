from typing import Any
from .registry import ProviderRegistry
from .base import BaseLLMProvider


class ProviderFactory:
    """
    Factory for creating LLM providers dynamically.
    """

    @staticmethod
    def create(name: str, model: str, **kwargs: Any) -> BaseLLMProvider:
        provider_cls = ProviderRegistry.get(name)
        return provider_cls(model=model, **kwargs)
