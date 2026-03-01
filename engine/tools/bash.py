from __future__ import annotations

import asyncio
import subprocess

from .base import BaseTool, ToolExecutionResult


class BashTool(BaseTool):
    name = "bash"
    description = "Execute shell commands."
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "restart": {"type": "boolean"},
        },
        "required": [],
    }
    timeout_seconds = 90

    async def execute(self, arguments: dict) -> ToolExecutionResult:
        # Backward-compatible with prior persistent-session contract.
        if bool(arguments.get("restart", False)):
            return ToolExecutionResult(success=True, output="bash session restarted")

        command = arguments.get("command")
        if not command:
            return ToolExecutionResult(
                success=False,
                error="Missing 'command'. Provide {'command': '<shell command>'}",
            )

        try:
            completed = await asyncio.to_thread(
                subprocess.run,
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return ToolExecutionResult(
                success=False,
                error=f"bash command timed out after {self.timeout_seconds}s",
            )
        except Exception as exc:
            return ToolExecutionResult(success=False, error=str(exc) or repr(exc))

        stderr = (completed.stderr or "").strip() or None
        stdout = (completed.stdout or "").strip() or None
        success = completed.returncode == 0

        return ToolExecutionResult(
            success=success,
            output=stdout,
            error=stderr,
            metadata={"returncode": completed.returncode},
        )
