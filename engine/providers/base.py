from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LLMMessage:
    role: str
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None


@dataclass
class LLMToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    content: Optional[str]
    tool_calls: List[LLMToolCall]
    raw: Any


@dataclass
class LLMRequest:
    messages: List[LLMMessage]
    tools: Optional[List[Dict[str, Any]]] = None
    temperature: float = 0.2
    max_tokens: Optional[int] = 4096


class BaseLLMProvider(ABC):
    def __init__(self, model: str, **kwargs: Any):
        self.model = model
        self.config = kwargs

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError
