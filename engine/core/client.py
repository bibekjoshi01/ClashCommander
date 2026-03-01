from mistralai import Mistral
from typing import List, Dict, Any
from .config import MISTRAL_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE


class MistralClient:
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY not set")
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    async def chat(self, messages: List[Dict[str, Any]], tools: List[Dict]):
        response = await self.client.chat.complete_async(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return response
