from __future__ import annotations

import asyncio
import os

from .base import BaseTool, ToolExecutionResult


class _BashSession:
    command = "/bin/bash"
    sentinel = "<<engine-bash-exit>>"

    def __init__(self, timeout_seconds: float = 90.0, output_delay: float = 0.2):
        self.timeout_seconds = timeout_seconds
        self.output_delay = output_delay
        self._process: asyncio.subprocess.Process | None = None
        self._timed_out = False

    async def start(self) -> None:
        if self._process and self._process.returncode is None:
            return
        self._process = await asyncio.create_subprocess_shell(
            self.command,
            preexec_fn=os.setsid,
            shell=True,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            bufsize=0,
        )
        self._timed_out = False

    def stop(self) -> None:
        if not self._process:
            return
        if self._process.returncode is None:
            self._process.terminate()

    async def run(self, command: str) -> ToolExecutionResult:
        if not self._process or self._process.returncode is not None:
            await self.start()

        if self._timed_out:
            return ToolExecutionResult(
                success=False,
                error=(
                    "bash session timed out previously; call bash with "
                    "{'restart': true} to continue"
                ),
            )

        assert self._process is not None
        assert self._process.stdin is not None
        assert self._process.stdout is not None
        assert self._process.stderr is not None

        self._process.stdin.write(
            command.encode() + f"; echo '{self.sentinel}'\n".encode()
        )
        await self._process.stdin.drain()

        try:
            async with asyncio.timeout(self.timeout_seconds):
                while True:
                    await asyncio.sleep(self.output_delay)
                    out = self._process.stdout._buffer.decode()  # pyright: ignore[reportAttributeAccessIssue]
                    if self.sentinel in out:
                        out = out[: out.index(self.sentinel)]
                        break
        except asyncio.TimeoutError:
            self._timed_out = True
            return ToolExecutionResult(
                success=False,
                error=f"bash command timed out after {self.timeout_seconds}s",
            )

        err = self._process.stderr._buffer.decode()  # pyright: ignore[reportAttributeAccessIssue]

        self._process.stdout._buffer.clear()  # pyright: ignore[reportAttributeAccessIssue]
        self._process.stderr._buffer.clear()  # pyright: ignore[reportAttributeAccessIssue]

        return ToolExecutionResult(
            success=True,
            output=out.rstrip("\n"),
            error=err.rstrip("\n") or None,
        )


class BashTool(BaseTool):
    name = "bash"
    description = "Execute shell commands in a persistent bash session."
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "restart": {"type": "boolean"},
        },
        "required": [],
    }

    def __init__(self):
        self._session = _BashSession()

    async def execute(self, arguments: dict) -> ToolExecutionResult:
        restart = bool(arguments.get("restart", False))
        command = arguments.get("command")

        if restart:
            self._session.stop()
            self._session = _BashSession()
            await self._session.start()
            return ToolExecutionResult(success=True, output="bash session restarted")

        if not command:
            return ToolExecutionResult(
                success=False,
                error="Missing 'command'. Provide {'command': '<shell command>'}",
            )

        return await self._session.run(command)

    async def close(self) -> None:
        self._session.stop()
