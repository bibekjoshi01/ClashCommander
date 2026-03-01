from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResponse:
    tool_call_id: str
    output: Optional[str] = None
    image_base64: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AgentMessage:
    role: str
    content: Any
