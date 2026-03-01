from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Dict


@dataclass
class ToolExecutionResult:
    """
    Standardized output format for all tools.
    """

    success: bool = True
    output: Any = None  # textual or structured output
    error: Optional[str] = None  # error message if failed
    screenshot_base64: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """
    Abstract base class for any tool callable by the LLM.
    """

    name: str
    description: str
    parameters: Dict[str, Any]

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with validated arguments.
        Must return JSON-serializable result.
        """
        pass

    def to_schema(self) -> Dict[str, Any]:
        """
        Convert tool definition into OpenAI-compatible function schema.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
