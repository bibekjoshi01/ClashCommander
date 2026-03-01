from __future__ import annotations

import asyncio
import os
from typing import Iterable, Optional

from engine.core.agent_loop import QAOrchestrator
from engine.core.types import QAResult, QATask
from engine.prompts import build_system_prompt, build_user_prompt
from engine.providers import ProviderFactory
from engine.core.config import get_settings

from engine.tools import (
    BaseTool,
    BashTool,
    ConsoleNetworkAuditTool,
    PageAuditTool,
    PerformanceAuditTool,
    PlaywrightComputerTool,
    SecurityHeadersAuditTool,
    ToolCollection,
)

DEFAULT_QA_TASK = "Explore main user flows and report functional, UX, accessibility, performance, and security issues."


class Engine:
    """Modular QA engine that can be called from any backend service."""

    def __init__(
        self,
        *,
        provider_name: str = "mistral",
        model: str = "mistral-large-latest",
        provider_kwargs: Optional[dict] = None,
        tools: Optional[Iterable[BaseTool]] = None,
        max_iterations: int = 20,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        locale: str = "en-US",
        device_profile: str = "iphone_14",
        network_profile: str = "wifi",
    ):
        provider_kwargs = provider_kwargs or {}
        settings = get_settings()

        if provider_name == "mistral":
            provider_kwargs["api_key"] = settings.MISTRAL_API_KEY
        if provider_name == "huggingface":
            api_key = settings.HUGGINGFACE_API_KEY
            if not api_key:
                raise ValueError(
                    "Hugging Face API key not set. Set HUGGINGFACE_API_KEY in your environment."
                )
            provider_kwargs["api_key"] = api_key

        self.provider = ProviderFactory.create(
            name=provider_name,
            model=model,
            **provider_kwargs,
        )

        self.max_iterations = max_iterations
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.locale = locale
        self.device_profile = device_profile
        self.network_profile = network_profile

        self._tools = list(tools) if tools is not None else []

    def _build_default_tools(self, target_url: str) -> ToolCollection:
        if self._tools:
            return ToolCollection(self._tools)

        if PlaywrightComputerTool is None:
            raise RuntimeError(
                "Playwright is not installed. Install it to use the default 'computer' tool."
            )
        if (
            PageAuditTool is None
            or ConsoleNetworkAuditTool is None
            or PerformanceAuditTool is None
            or SecurityHeadersAuditTool is None
        ):
            raise RuntimeError(
                "Audit tools unavailable because Playwright-dependent modules failed to load."
            )

        computer_tool = PlaywrightComputerTool(
            target_url=target_url,
            locale=self.locale,
            device_profile=self.device_profile,
            network_profile=self.network_profile,
        )

        return ToolCollection(
            [
                computer_tool,
                BashTool(),
                PageAuditTool(computer_tool=computer_tool),
                ConsoleNetworkAuditTool(computer_tool=computer_tool),
                PerformanceAuditTool(computer_tool=computer_tool),
                SecurityHeadersAuditTool(fallback_url=target_url),
            ]
        )

    async def run_task(self, task: QATask) -> QAResult:
        tools = self._build_default_tools(task.target_url)
        system_prompt = build_system_prompt(
            tools=[tools.get(n) for n in tools.list_names()],
            locale=self.locale,
            device_profile=self.device_profile,
            network_profile=self.network_profile,
        )
        user_prompt = build_user_prompt(
            target_url=task.target_url,
            task=task.task,
            context=task.context,
        )

        orchestrator = QAOrchestrator(
            provider=self.provider,
            tools=tools,
            max_iterations=self.max_iterations,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        try:
            return await orchestrator.execute(
                system_prompt=system_prompt, user_prompt=user_prompt
            )
        finally:
            await tools.close()

    async def run_url(self, target_url: str, task: Optional[str] = None) -> QAResult:
        qa_task = QATask(target_url=target_url, task=task or DEFAULT_QA_TASK)
        return await self.run_task(qa_task)


async def run_qa_engine(
    target_url: str,
    provider_name: str = "mistral",
    model: str = "mistral-large-latest",
    provider_kwargs: Optional[dict] = None,
    max_iterations: int = 20,
    locale: str = "en-US",
    persona: Optional[str] = None,
    device_profile: str = "iphone_14",
    network_profile: str = "wifi",
) -> QAResult:
    engine = Engine(
        provider_name=provider_name,
        model=model,
        provider_kwargs=provider_kwargs,
        max_iterations=max_iterations,
        locale=locale,
        persona=persona,
        device_profile=device_profile,
        network_profile=network_profile,
    )
    return await engine.run_url(target_url)


def run_qa_engine_sync(*args, **kwargs) -> QAResult:
    return asyncio.run(run_qa_engine(*args, **kwargs))


__all__ = [
    "Engine",
    "QATask",
    "QAResult",
    "run_qa_engine",
    "run_qa_engine_sync",
]
