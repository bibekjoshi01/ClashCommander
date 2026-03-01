from __future__ import annotations

from typing import List

from engine.providers.base import BaseLLMProvider, LLMMessage, LLMRequest
from engine.tools.base import ToolExecutionResult
from engine.tools.collection import ToolCollection

from .parsing import extract_issues
from .types import QAResult


class QAOrchestrator:
    """Provider-agnostic orchestration loop for model + tools."""

    def __init__(
        self,
        provider: BaseLLMProvider,
        tools: ToolCollection,
        max_iterations: int = 20,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ):
        self.provider = provider
        self.tools = tools
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def execute(self, system_prompt: str, user_prompt: str) -> QAResult:
        result = QAResult()
        messages: List[LLMMessage] = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        for step in range(1, self.max_iterations + 1):
            response = await self.provider.generate(
                LLMRequest(
                    messages=messages,
                    tools=self.tools.list_schemas(),
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
            )

            assistant_content = response.content or ""
            messages.append(LLMMessage(role="assistant", content=assistant_content))
            result.raw_model_output = assistant_content

            result.trace.append(
                {
                    "step": step,
                    "assistant_content": assistant_content,
                    "tool_calls": [
                        {"id": c.id, "name": c.name, "arguments": c.arguments}
                        for c in response.tool_calls
                    ],
                }
            )

            if not response.tool_calls:
                break

            for call in response.tool_calls:
                tool_result = await self._safe_tool_execute(call.name, call.arguments)
                result.tool_outputs.append(tool_result)

                if tool_result.screenshot_base64:
                    result.screenshots.append(tool_result.screenshot_base64)

                messages.append(
                    LLMMessage(
                        role="tool",
                        name=call.name,
                        tool_call_id=call.id,
                        content=self._tool_result_to_message(tool_result),
                    )
                )

        parsed_issues = extract_issues(result.raw_model_output)
        if parsed_issues:
            result.issues = parsed_issues

        return result

    async def _safe_tool_execute(self, name: str, arguments: dict) -> ToolExecutionResult:
        try:
            return await self.tools.run(name=name, arguments=arguments)
        except Exception as exc:
            return ToolExecutionResult(success=False, error=str(exc))

    def _tool_result_to_message(self, tool_result: ToolExecutionResult) -> str:
        if tool_result.success:
            if tool_result.output:
                return tool_result.output
            if tool_result.screenshot_base64:
                return "Screenshot captured"
            return "Tool executed successfully"
        return f"Tool execution failed: {tool_result.error or 'unknown error'}"
