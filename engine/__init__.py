import asyncio
from typing import Optional, List

from engine.providers.factory import ProviderFactory
from engine.tools.registry import ToolRegistry
from engine.core.agent_loop import QAOrchestrator
from engine.core.types import QAResult
from engine.prompts.qa_prompts import build_system_prompt, build_user_prompt


class Engine:
    """
    AI-powered agentic QA engine.
    Backend calls this class for any request.

    Features:
    - Supports any registered LLM provider (Mistral, OpenAI, local, etc.)
    - Automatically loads all registered tools
    - Fully async agent loop via QAOrchestrator
    - Collects structured results, screenshots, and issues
    """

    def __init__(
        self,
        provider_name: str = "mistral",
        model: str = "mistral-large",
        provider_kwargs: Optional[dict] = None,
        max_iterations: int = 15,
    ):
        # Initialize the provider dynamically
        self.provider = ProviderFactory.create(
            name=provider_name, model=model, **(provider_kwargs or {})
        )
        # Load all registered tools
        self.tools: List = list(ToolRegistry._tools.values())
        self.max_iterations = max_iterations

    async def run(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> QAResult:
        """
        Execute the QA agent loop with given prompts.
        """
        orchestrator = QAOrchestrator(
            provider=self.provider,
            tools=self.tools,
            max_iterations=self.max_iterations,
        )
        return await orchestrator.execute(
            system_prompt=system_prompt, user_prompt=user_prompt
        )

    async def run_url(self, target_url: str) -> QAResult:
        """
        Quick entrypoint for a URL.
        Builds system and user prompts automatically and runs the orchestrator.
        """
        system_prompt = build_system_prompt(
            tools=[tool.to_schema() for tool in self.tools]
        )
        user_prompt = build_user_prompt(target_url)
        return await self.run(system_prompt=system_prompt, user_prompt=user_prompt)


async def run_qa_engine(
    target_url: str,
    provider_name: str = "mistral",
    model: str = "mistral-large",
    provider_kwargs: Optional[dict] = None,
    max_iterations: int = 15,
) -> QAResult:
    """
    Quick one-shot async entrypoint.
    Auto-loads tools, builds prompts, and runs QA loop.
    """
    engine = Engine(
        provider_name=provider_name,
        model=model,
        provider_kwargs=provider_kwargs,
        max_iterations=max_iterations,
    )
    return await engine.run_url(target_url)


def run_qa_engine_sync(*args, **kwargs) -> QAResult:
    return asyncio.run(run_qa_engine(*args, **kwargs))
