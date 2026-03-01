from typing import Dict, List
from .base import BaseTool


class ToolRegistry:
    """
    Central registry for all available tools.
    """

    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool) -> None:
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> BaseTool:
        if name not in cls._tools:
            raise ValueError(f"Tool '{name}' not registered.")
        return cls._tools[name]

    @classmethod
    def list_schemas(cls) -> List[Dict]:
        return [tool.to_schema() for tool in cls._tools.values()]

    @classmethod
    def list_names(cls) -> List[str]:
        return list(cls._tools.keys())
