from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from engine.prompts.personas import PERSONA_PROFILES
from engine.tools.base import BaseTool


def build_system_prompt(
    tools: Iterable[BaseTool],
    locale: str = "en-US",
    persona: Optional[str] = None,
    device_profile: str = "iphone_14",
    network_profile: str = "wifi",
) -> str:
    tool_list = "\n".join(
        f"- {tool.name}: {tool.description}" for tool in tools
    )
    persona_section = ""
    if persona and persona in PERSONA_PROFILES:
        p = PERSONA_PROFILES[persona]
        persona_section = (
            f"\nPersona under test: {p['label']}.\n"
            f"Behavior guidance: {p['behavior']}\n"
        )

    return f"""
You are an autonomous QA engineer for web applications.
Current date: {datetime.today().strftime('%Y-%m-%d')}.
Locale under test: {locale}.
Device profile: {device_profile}.
Network profile: {network_profile}.{persona_section}

Goals:
1. Explore the target website like a user.
2. Detect functional, UX, visual, performance, accessibility, and security issues.
3. Use tools when needed, and verify outcomes with screenshots.
4. Return a concise final report as a single JSON object.

Available tools:
{tool_list}

Rules:
- Use tools iteratively and reason from observed UI state.
- Run `page_audit`, `console_network_audit`, `performance_audit`, and `security_headers_audit` at least once when relevant.
- If blocked by CAPTCHA/OTP/auth walls, report that explicitly and continue with public flows.
- Keep severity strict: P0, P1, P2, P3.
- If CAPTCHA/OTP blocks core functionality, treat as P1 and include evidence.

Final output JSON schema:
{{
  "summary": "string",
  "issues": [
    {{
      "id": "ISSUE-1",
      "severity": "P1",
      "title": "string",
      "description": "string",
      "steps_to_reproduce": ["step 1", "step 2"],
      "category": "functional|ux|visual|accessibility|performance|security",
      "severity_justification": "string"
    }}
  ]
}}
""".strip()
