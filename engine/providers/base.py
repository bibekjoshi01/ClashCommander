from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    name: Optional[str] = None


@dataclass
class LLMToolCall:
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    content: Optional[str]
    tool_calls: Optional[List[LLMToolCall]]
    raw: Any  # raw provider response for debugging/trace


@dataclass
class LLMRequest:
    messages: List[LLMMessage]
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    tools: Optional[List[Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """
    Abstract interface for any LLM provider (Mistral, OpenAI-compatible, local).
    """

    def __init__(self, model: str, **kwargs: Any):
        self.model = model
        self.config = kwargs

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Execute a single model call.
        Must:
            - handle tool call format mapping
            - normalize provider-specific schema
            - return standardized LLMResponse
        """
        raise NotImplementedError

    async def healthcheck(self) -> bool:
        """
        Optional healthcheck override.
        """
        try:
            test_request = LLMRequest(
                messages=[LLMMessage(role="user", content="ping")],
                max_tokens=5,
            )
            await self.generate(test_request)
            return True
        except Exception:
            return False
