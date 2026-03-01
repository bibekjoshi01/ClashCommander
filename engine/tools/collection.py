from __future__ import annotations

from typing import Dict, Iterable, List

from .base import BaseTool, ToolExecutionResult


class ToolCollection:
    """Runtime registry and executor for tool instances."""

    def __init__(self, tools: Iterable[BaseTool]):
        tool_map: Dict[str, BaseTool] = {}
        for tool in tools:
            if tool.name in tool_map:
                raise ValueError(f"Duplicate tool name: {tool.name}")
            tool_map[tool.name] = tool
        self._tools = tool_map

    def get(self, name: str) -> BaseTool:
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not registered")
        return tool

    def list_schemas(self) -> List[Dict]:
        return [tool.to_schema() for tool in self._tools.values()]

    def list_names(self) -> List[str]:
        return list(self._tools.keys())

    async def run(self, name: str, arguments: Dict) -> ToolExecutionResult:
        tool = self.get(name)
        return await tool.execute(arguments)

    async def close(self) -> None:
        for tool in self._tools.values():
            await tool.close()
