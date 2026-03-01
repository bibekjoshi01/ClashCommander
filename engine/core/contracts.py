from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Literal


Role = Literal["system", "user", "assistant", "tool"]


@dataclass
class AgentMessage:
    role: Role
    content: str
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    tool_call_id: str
    name: str
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentResponse:
    message: AgentMessage
    tool_calls: Optional[List[ToolCall]] = None
    raw: Optional[Any] = None


@dataclass
class EngineResult:
    final_message: AgentMessage
    tool_results: List[ToolResult]
    trace: Optional[List[Any]] = None
