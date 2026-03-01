from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolExecutionResult:
    """Standardized output format for all tools."""

    success: bool = True
    output: Optional[str] = None
    error: Optional[str] = None
    screenshot_base64: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """Base interface for tools callable by the model."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    timeout_seconds: int = 30

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolExecutionResult:
        raise NotImplementedError

    def to_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }

    async def close(self) -> None:
        """Optional cleanup hook for stateful tools."""
        return None
