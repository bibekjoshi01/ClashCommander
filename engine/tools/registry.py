from typing import Dict
from .base import BaseTool


class ToolRegistry:
    def __init__(self, tools: list[BaseTool]):
        self._tools: Dict[str, BaseTool] = {tool.name: tool for tool in tools}

    def list_schemas(self):
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema,
            }
            for tool in self._tools.values()
        ]

    async def execute(self, name: str, input_data: dict):
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        return await tool.execute(input_data)
