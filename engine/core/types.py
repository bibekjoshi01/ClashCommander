from dataclasses import dataclass
from typing import List, Optional, Dict, Any


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
    """
    Engine result.
    """

    issues: List[QAIssue]
    raw_model_output: Optional[str]
