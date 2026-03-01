from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from engine.tools.base import ToolExecutionResult


@dataclass
class QATask:
    """Input for a QA run."""

    target_url: str
    task: str = "Explore the main user flow and report functional, UX, and accessibility issues."
    context: Optional[Dict[str, Any]] = None


@dataclass
class QAIssue:
    """Single issue reported by the agent."""

    title: str
    severity: str
    description: str
    category: Optional[str] = None
    steps_to_reproduce: Optional[List[str]] = None


@dataclass
class QAResult:
    """Structured result returned by the engine."""

    issues: List[Dict[str, Any]] = field(default_factory=list)
    raw_model_output: Optional[str] = None
    tool_outputs: List[ToolExecutionResult] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    trace: List[Dict[str, Any]] = field(default_factory=list)
