from mistralai import Mistral
from typing import List


class MistralProvider:
    def __init__(self, api_key: str, model: str = "codestral-latest"):
        self.client = Mistral(api_key=api_key)
        self.model = model

    async def chat(self, messages: List[dict], tools=None):
        response = await self.client.chat.complete_async(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        return response
