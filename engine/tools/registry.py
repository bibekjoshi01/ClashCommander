from typing import List
from .base import BaseTool


class ToolRegistry:
    def __init__(self, tools: List[BaseTool]):
        self.tools = {tool.name: tool for tool in tools}

    def get_schemas(self):
        return [tool.to_openai_tool_schema() for tool in self.tools.values()]

    async def execute(self, name: str, arguments: dict):
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return await tool.execute(arguments)
