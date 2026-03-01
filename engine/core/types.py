from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from engine.tools.base import ToolExecutionResult


@dataclass
class QATask:
    """
    Input for QA engine.
    """

    target_url: str
    html_snapshot: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class QAIssue:
    """
    Single detected issue.
    """

    title: str
    description: str
    severity: str  # low | medium | high | critical
    category: Optional[str] = None


@dataclass
class QAResult:
    issues: List[Dict[str, Any]] = field(default_factory=list)
    raw_model_output: Optional[str] = None
    tool_outputs: List[ToolExecutionResult] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
