from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
import asyncio


@dataclass
class ToolExecutionResult:
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    screenshot_base64: Optional[str] = None


class BaseTool(ABC):
    """
    Provider-agnostic tool contract.
    Strict-mode compliant.
    """

    name: str
    description: str
    input_schema: Dict[str, Any]
    timeout_seconds: int = 60  # default safety timeout

    def get_schema(self) -> Dict[str, Any]:
        """
        Returns JSON schema in provider-compatible format.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_schema,
        }

    async def run(self, input_data: Dict[str, Any]) -> ToolExecutionResult:
        """
        Public execution wrapper.
        Handles timeout and error normalization.
        """

        try:
            return await asyncio.wait_for(
                self.execute(input_data),
                timeout=self.timeout_seconds,
            )

        except asyncio.TimeoutError:
            return ToolExecutionResult(
                success=False,
                error=f"Tool '{self.name}' timed out after {self.timeout_seconds}s",
            )

        except Exception as e:
            return ToolExecutionResult(
                success=False,
                error=str(e),
            )

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> ToolExecutionResult:
        """
        Tool-specific implementation.
        Must return ToolExecutionResult.
        """
        raise NotImplementedError
