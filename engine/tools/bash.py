import asyncio
from .base import BaseTool, ToolExecutionResult


class BashTool(BaseTool):
    name = "bash"
    description = "Execute a bash command in the system shell."

    input_schema = {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    }

    async def execute(self, input_data: dict):
        command = input_data["command"]

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            return ToolExecutionResult(
                success=True,
                output=stdout.decode(),
                error=stderr.decode() if stderr else None,
            )

        except Exception as e:
            return ToolExecutionResult(
                success=False,
                error=str(e),
            )
