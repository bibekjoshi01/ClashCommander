from abc import ABC, abstractmethod
from typing import Dict, Any


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
