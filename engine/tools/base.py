from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

from .result import ToolResult


@dataclass
class ToolExecutionResult:
    success: bool
    output: str | None = None
    error: str | None = None
    metadata: dict | None = None
    screenshot_base64: str | None = None


class BaseTool(ABC):
    """Provider-agnostic tool interface."""

    name: str
    description: str
    input_schema: Dict[str, Any]

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> ToolExecutionResult: ...
