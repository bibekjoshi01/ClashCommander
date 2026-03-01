from typing import Dict, Any

from engine.providers.base import LLMToolCall
from engine.tools.registry import ToolRegistry


class ToolExecutor:
    """
    Responsible for safely executing tool calls from the LLM.
    """

    @staticmethod
    async def execute(tool_call: LLMToolCall) -> Dict[str, Any]:
        try:
            tool = ToolRegistry.get(tool_call.name)

            result = await tool.execute(tool_call.arguments)

            return {
                "success": True,
                "tool": tool_call.name,
                "result": result,
            }

        except Exception as e:
            # Never crash the agent loop
            return {
                "success": False,
                "tool": tool_call.name,
                "error": str(e),
            }
