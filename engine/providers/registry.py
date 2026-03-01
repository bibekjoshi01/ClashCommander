from typing import Type, Dict
from .base import BaseLLMProvider


class ProviderRegistry:
    """
    Central registry for all LLM providers.
    Enables dynamic provider loading without modifying engine core.
    """

    _registry: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: Type[BaseLLMProvider]) -> None:
        if name in cls._registry:
            raise ValueError(f"Provider '{name}' already registered.")
        cls._registry[name] = provider_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseLLMProvider]:
        if name not in cls._registry:
            raise ValueError(
                f"Provider '{name}' not found. "
                f"Available providers: {list(cls._registry.keys())}"
            )
        return cls._registry[name]

    @classmethod
    def list_providers(cls):
        return list(cls._registry.keys())
