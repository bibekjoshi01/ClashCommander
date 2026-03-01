from abc import ABC, abstractmethod
from typing import Dict, Any
from .result import ToolResult


class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        pass

    def to_openai_tool_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        }
