from __future__ import annotations

# Project Imports
from engine.core.agent_loop import QAOrchestrator
from engine.core.types import QAResult, QATask
from engine.prompts import build_system_prompt, build_user_prompt
from engine.providers import ProviderFactory
from engine.tools import (
    PlaywrightComputerTool,
    ToolCollection,
)

try:
    from engine.tools.console import ConsoleWatcherTool, NetworkMonitorTool
except ModuleNotFoundError:
    NetworkMonitorTool = None
    ConsoleWatcherTool = None

try:
    from engine.tools.functional import (
        ButtonClickCheckerTool,
        DeadLinkCheckerTool,
        FormValidatorTool,
        LoginFlowCheckerTool,
        SessionPersistenceCheckerTool,
    )
except ModuleNotFoundError:
    DeadLinkCheckerTool = None
    FormValidatorTool = None
    ButtonClickCheckerTool = None
    LoginFlowCheckerTool = None
    SessionPersistenceCheckerTool = None

try:
    from engine.tools.uiux import (
        AccessibilityAuditTool,
        ResponsiveLayoutCheckerTool,
        TouchTargetCheckerTool,
    )
except ModuleNotFoundError:
    AccessibilityAuditTool = None
    ResponsiveLayoutCheckerTool = None
    TouchTargetCheckerTool = None

try:
    from engine.tools.metadata import SEOMetadataCheckerTool
except ModuleNotFoundError:
    SEOMetadataCheckerTool = None

try:
    from engine.tools.performance import PerformanceAuditTool
except ModuleNotFoundError:
    PerformanceAuditTool = None

try:
    from engine.tools.security import (
        SecurityContentAuditTool,
        SecurityHeadersAuditTool,
        SSLAuditTool,
    )
except ModuleNotFoundError:
    SecurityContentAuditTool = None  # type: ignore[assignment]
    SecurityHeadersAuditTool = None
    SSLAuditTool = None


class Engine:
    """Modular QA engine that can be called from any backend service."""

    def __init__(
        self,
        *,
        provider_name: str = "mistral",
        model: str = "mistral-large-latest",
        provider_kwargs: dict | None = None,
        max_iterations: int = 20,
        temperature: float = 0.2,
        max_tokens: int = 10000,
        locale: str = "en-US",
        device_profile: str = "iphone_14",
        network_profile: str = "wifi",
    ):
        provider_kwargs = provider_kwargs or {}

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

    def _build_default_tools(self, target_url: str) -> ToolCollection:
        if PlaywrightComputerTool is None:
            raise RuntimeError(
                "Playwright is not installed. Install it to use browser-backed tools."
            )

        computer_tool = PlaywrightComputerTool(
            target_url=target_url,
            locale=self.locale,
            device_profile=self.device_profile,
            network_profile=self.network_profile,
        )

        tools = []
        if DeadLinkCheckerTool is not None:
            tools.append(DeadLinkCheckerTool(fallback_url=target_url))
        if FormValidatorTool is not None:
            tools.append(FormValidatorTool(fallback_url=target_url))
        if ButtonClickCheckerTool is not None:
            tools.append(ButtonClickCheckerTool(fallback_url=target_url))
        if LoginFlowCheckerTool is not None:
            tools.append(
                LoginFlowCheckerTool(
                    computer_tool=computer_tool, fallback_url=target_url
                )
            )
        if SessionPersistenceCheckerTool is not None:
            tools.append(
                SessionPersistenceCheckerTool(
                    computer_tool=computer_tool, fallback_url=target_url
                )
            )

        if AccessibilityAuditTool is not None:
            tools.append(AccessibilityAuditTool(fallback_url=target_url))
        if ResponsiveLayoutCheckerTool is not None:
            tools.append(ResponsiveLayoutCheckerTool(fallback_url=target_url))
        if TouchTargetCheckerTool is not None:
            tools.append(TouchTargetCheckerTool(fallback_url=target_url))

        if NetworkMonitorTool is not None:
            tools.append(NetworkMonitorTool(computer_tool=computer_tool))
        if ConsoleWatcherTool is not None:
            tools.append(ConsoleWatcherTool(computer_tool=computer_tool))
        if SEOMetadataCheckerTool is not None:
            tools.append(SEOMetadataCheckerTool(computer_tool=computer_tool))
        if PerformanceAuditTool is not None:
            tools.append(PerformanceAuditTool(computer_tool=computer_tool))

        if SSLAuditTool is not None:
            tools.append(SSLAuditTool(fallback_url=target_url))
        if SecurityHeadersAuditTool is not None:
            tools.append(SecurityHeadersAuditTool(fallback_url=target_url))
        if SecurityContentAuditTool is not None:
            tools.append(SecurityContentAuditTool(computer_tool=computer_tool))

        if not tools:
            raise RuntimeError(
                "No tools available. Check optional dependencies and tool modules."
            )
        return ToolCollection(tools)

    async def run_task(self, task: QATask) -> QAResult:
        # Build tools
        tools = self._build_default_tools(task.target_url)

        # System Prompt
        system_prompt = build_system_prompt(
            tools=[tools.get(n) for n in tools.list_names()],
            locale=self.locale,
            device_profile=self.device_profile,
            network_profile=self.network_profile,
        )

        # User Prompt
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


__all__ = ["Engine", "QATask", "QAResult"]
