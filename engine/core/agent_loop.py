from typing import List

from engine.providers.base import BaseLLMProvider, LLMRequest, LLMMessage
from engine.tools.base import BaseTool
from .types import QAResult


class QAOrchestrator:
    """
    Core agent loop.

    Responsible for:
    - Iterative LLM calls
    - Tool execution
    - Conversation state management
    """

    def __init__(
        self,
        provider: BaseLLMProvider,
        tools: List[BaseTool],
        max_iterations: int = 15,
    ):
        self.provider = provider
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations

    async def execute(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> QAResult:
        """
        Executes full agent loop.
        """

        messages: List[LLMMessage] = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]

        for iteration in range(self.max_iterations):

            request = LLMRequest(messages=messages)
            response = await self.provider.generate(request)

            # Append assistant message
            messages.append(
                LLMMessage(
                    role="assistant",
                    content=response.content,
                )
            )

            # If no tool calls → finished
            if not response.tool_calls:
                break

            # Execute tool calls
            for tool_call in response.tool_calls:
                tool = self.tools.get(tool_call.name)

                if not tool:
                    raise RuntimeError(f"Tool '{tool_call.name}' not registered.")

                result = await tool.execute(tool_call.arguments)

                messages.append(
                    LLMMessage(
                        role="tool",
                        name=tool_call.name,
                        content=result,
                    )
                )

        # Final response content = last assistant message
        final_content = messages[-1].content if messages else None

        return QAResult(
            issues=[],
            raw_model_output=final_content,
        )
