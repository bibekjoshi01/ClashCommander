from typing import Optional
from engine.providers.factory import ProviderFactory
from engine.tools.registry import ToolRegistry
from engine.core.agent_loop import QAOrchestrator
from engine.core.types import QAResult


class Engine:
    """
    AI-powered agentic QA engine.
    Backend calls this class for any request.
    """

    def __init__(
        self,
        provider_name: str,
        model: str,
        provider_kwargs: Optional[dict] = None,
        max_iterations: int = 15,
    ):
        self.provider = ProviderFactory.create(
            name=provider_name, model=model, **(provider_kwargs or {})
        )
        self.tools = list(ToolRegistry._tools.values())
        self.max_iterations = max_iterations

    async def run(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> QAResult:
        orchestrator = QAOrchestrator(
            provider=self.provider,
            tools=self.tools,
            max_iterations=self.max_iterations,
        )
        result = await orchestrator.execute(system_prompt, user_prompt)
        return result
