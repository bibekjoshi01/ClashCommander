from __future__ import annotations

import asyncio
import requests
from typing import Any, Optional

from .base import BaseLLMProvider, LLMRequest, LLMResponse
from .registry import ProviderRegistry


class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face Inference API provider for testing."""

    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs: Any,
    ):
        super().__init__(model=model, **kwargs)
        if not api_key:
            raise ValueError("Missing required provider config: api_key")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.endpoint = f"https://api-inference.huggingface.co/models/{model}"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        # Combine messages into a single prompt
        prompt = "\n".join([msg.content for msg in request.messages])

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": prompt}

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        self.endpoint,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout,
                    ),
                )
                response.raise_for_status()
                data = response.json()
                text = (
                    data[0]["generated_text"] if isinstance(data, list) else str(data)
                )

                # Hugging Face has no tool calls; return empty list
                return LLMResponse(
                    content=text,
                    tool_calls=[],
                    raw=data,
                )
            except Exception as err:
                last_error = err
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * attempt)

        raise RuntimeError(
            f"Hugging Face provider failed after {self.max_retries} attempts"
        ) from last_error


ProviderRegistry.register("huggingface", HuggingFaceProvider)
