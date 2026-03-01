from __future__ import annotations

import json
from typing import Any

from ..base import BaseTool, ToolExecutionResult
from ..playwright import PlaywrightComputerTool


class ConsoleWatcherTool(BaseTool):
    """Collect browser console messages and summarize errors/warnings."""

    name = "console_watcher"
    description = "Collect recent browser console messages (errors/warnings/info)."
    timeout_seconds = 20
    input_schema = {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            "level_filter": {"type": "string"},
        },
        "required": [],
    }

    def __init__(self, computer_tool: PlaywrightComputerTool):
        self._computer = computer_tool

    async def execute(self, arguments: dict[str, Any]) -> ToolExecutionResult:
        limit = int(arguments.get("limit", 200))
        await self._computer.ensure_ready()

        try:
            events: list[str] = await self._computer.get_console_events(limit=limit)
        except Exception as exc:  # pragma: no cover - defensive
            return ToolExecutionResult(
                success=False, error=f"Failed to fetch console events: {exc}"
            )

        # Classify events simply by prefix "[type]"
        errors = [e for e in events if e.startswith("[error]") or e.startswith("[pageerror]")]
        warnings = [e for e in events if e.startswith("[warning]")]
        logs = [e for e in events if e.startswith("[log]") or e.startswith("[info]")]

        top_errors = errors[:10]
        top_warnings = warnings[:10]

        findings: list[str] = []
        if errors:
            findings.append(f"{len(errors)} console error(s) detected")
        if warnings and not errors:
            findings.append(f"{len(warnings)} console warning(s) detected")
        if not findings:
            findings = ["No console errors or warnings detected"]

        payload = {
            "url": self._computer.current_url,
            "total_console_events": len(events),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "log_count": len(logs),
            "top_errors": top_errors,
            "top_warnings": top_warnings,
            "findings": findings,
        }

        return ToolExecutionResult(
            success=True,
            output=json.dumps(payload),
            metadata={
                "url": self._computer.current_url,
                "console_event_count": len(events),
            },
        )


class NetworkMonitorTool(BaseTool):
    """Collect failed requests and summary network metrics for current page."""

    name = "network_monitor"
    description = (
        "Collect failed network requests (Playwright requestfailed), resource counts, "
        "and basic slow-resource heuristics."
    )
    timeout_seconds = 30
    input_schema = {
        "type": "object",
        "properties": {
            "slow_threshold_ms": {"type": "integer", "minimum": 50},
            "scan_resources": {"type": "boolean"},
        },
        "required": [],
    }

    def __init__(self, computer_tool: PlaywrightComputerTool):
        self._computer = computer_tool

    async def execute(self, arguments: dict[str, Any]) -> ToolExecutionResult:
        slow_threshold = int(arguments.get("slow_threshold_ms", 1000))
        scan_resources = bool(arguments.get("scan_resources", True))

        await self._computer.ensure_ready()

        try:
            failures = await self._computer.get_request_failures(limit=500)
        except Exception as exc:  # pragma: no cover - defensive
            failures = []
            failure_err = str(exc)
        else:
            failure_err = None

        try:
            perf = await self._computer.collect_perf_metrics()
        except Exception as exc:  # pragma: no cover - defensive
            return ToolExecutionResult(
                success=False, error=f"Failed to collect perf metrics: {exc}"
            )

        resource_count = perf.get("resource_count")
        total_transfer_kb = perf.get("total_transfer_kb")

        findings: list[str] = []
        if failures:
            findings.append(f"{len(failures)} failed network request(s) detected")
        if resource_count and resource_count > 200:
            findings.append(f"High resource count: {resource_count}")
        if total_transfer_kb and total_transfer_kb > 2048:
            findings.append(f"Large total transferred bytes: {int(total_transfer_kb)} KB")

        slow_hint = []
        if scan_resources:
            # collect_perf_metrics does not return per-resource durations in current tooling,
            # so attempt a lightweight page evaluate for resource durations (best-effort).
            try:
                # This evaluate returns array of {name, duration, transferSize} for resources > slow_threshold
                script = f"""
                () => {{
                    try {{
                        const out = [];
                        const resources = performance.getEntriesByType('resource') || [];
                        for (const r of resources) {{
                            const dur = r.duration || 0;
                            if (dur >= {slow_threshold}) {{
                                out.push({{name: r.name, duration: Math.round(dur), transferSize: r.transferSize || 0}});
                            }}
                        }}
                        return out.slice(0, 50);
                    }} catch (e) {{
                        return [];
                    }}
                }}
                """
                slow_resources = await self._computer._page.evaluate(script)  # noqa: SLF001 - best-effort use of page
            except Exception:
                slow_resources = []
            if slow_resources:
                slow_hint = slow_resources
                findings.append(f"{len(slow_resources)} resources slower than {slow_threshold}ms")
        # Build result payload
        payload = {
            "url": self._computer.current_url,
            "failed_requests": failures,
            "resource_count": resource_count,
            "total_transfer_kb": total_transfer_kb,
            "slow_resources": slow_hint,
            "findings": findings or ["No network issues detected"],
        }

        meta = {"url": self._computer.current_url}
        if failure_err:
            meta["failure_warning"] = failure_err

        return ToolExecutionResult(
            success=True,
            output=json.dumps(payload),
            metadata=meta,
        )
