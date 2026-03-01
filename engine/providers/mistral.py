import asyncio
from typing import Any, Dict, List, Optional

from mistralai import Mistral

from .base import (
    BaseLLMProvider,
    LLMRequest,
    LLMResponse,
    LLMMessage,
    LLMToolCall,
)
from .registry import ProviderRegistry


class MistralProvider(BaseLLMProvider):
    """
    Async Mistral provider implementation.
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: int = 60,
        max_retries: int = 3,
        **kwargs: Any,
    ):
        super().__init__(model=model, **kwargs)
        self.client = Mistral(api_key=api_key)
        self.timeout = timeout
        self.max_retries = max_retries

    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = self._convert_messages(request.messages)

        attempt = 0
        last_exception: Optional[Exception] = None

        while attempt < self.max_retries:
            try:
                response = await asyncio.wait_for(
                    self.client.chat.complete_async(
                        model=self.model,
                        messages=messages,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                        tools=request.tools,
                        response_format=request.response_format,
                    ),
                    timeout=self.timeout,
                )

                return self._normalize_response(response)

            except Exception as e:
                last_exception = e
                attempt += 1
                await asyncio.sleep(0.5 * attempt)

        raise RuntimeError(
            f"MistralProvider failed after {self.max_retries} attempts"
        ) from last_exception

    def _convert_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        return [
            {
                "role": msg.role,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
            }
            for msg in messages
        ]

    def _normalize_response(self, response: Any) -> LLMResponse:
        choice = response.choices[0]
        message = choice.message

        content = message.content

        tool_calls: Optional[List[LLMToolCall]] = None

        if getattr(message, "tool_calls", None):
            tool_calls = [
                LLMToolCall(
                    name=tool_call.function.name,
                    arguments=tool_call.function.arguments,
                )
                for tool_call in message.tool_calls
            ]

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            raw=response,
        )


ProviderRegistry.register("mistral", MistralProvider)
