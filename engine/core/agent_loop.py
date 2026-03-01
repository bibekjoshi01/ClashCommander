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
        qa_result = QAResult()

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

                tool_result = await tool.execute(tool_call.arguments)

                # Append tool output to messages for LLM context
                messages.append(
                    LLMMessage(
                        role="tool",
                        name=tool_call.name,
                        content=(
                            tool_result.output
                            if hasattr(tool_result, "output")
                            else str(tool_result)
                        ),
                    )
                )

                # Collect structured tool result into QAResult
                qa_result.tool_outputs.append(tool_result)

                # Collect screenshots if available
                if getattr(tool_result, "screenshot_base64", None):
                    qa_result.screenshots.append(tool_result.screenshot_base64)

                # Collect issues if the tool provides them
                if getattr(tool_result, "issues", None):
                    qa_result.issues.extend(tool_result.issues)

        # Final response content = last assistant message
        final_content = messages[-1].content if messages else None
        qa_result.raw_model_output = final_content

        return qa_result
