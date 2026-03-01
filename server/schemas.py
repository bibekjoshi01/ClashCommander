from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QARequest(BaseModel):
    url: str = Field(..., description="Website URL to test")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context for QA flow (credentials, test notes, etc.)",
    )
    device_profile: str = Field(default="iphone_14")
    network_profile: str = Field(default="wifi")


class QAResponse(BaseModel):
    url: str
    issues: List[Dict[str, Any]]
    tool_outputs: List[Dict[str, Any]]
    screenshots: List[str]
    raw_model_output: Optional[str]
    trace: List[Dict[str, Any]]
