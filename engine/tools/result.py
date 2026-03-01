from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolResult:
    output: Optional[str] = None
    image_base64: Optional[str] = None
    error: Optional[str] = None
