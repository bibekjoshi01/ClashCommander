import json

import pytest

from engine.tools.functional_tools import LoginFlowCheckerTool


class _FakeComputer:
    def __init__(self):
        self.current_url = "https://example.com/login"

    async def ensure_ready(self):
        return None

    async def navigate(self, url: str):
        self.current_url = url

    async def inspect_login_surface(self):
        return {
            "password_input_count": 1,
            "email_or_user_input_count": 1,
            "forms_with_password_count": 1,
        }

    async def attempt_login(self, username: str, password: str):
        assert username == "user@example.com"
        assert password == "secret"
        return {
            "before_url": "https://example.com/login",
            "after_url": "https://example.com/dashboard",
            "username_filled": True,
            "password_filled": True,
            "submitted": True,
            "added_cookie_names": ["sessionid"],
            "error_text_detected": False,
            "likely_success": True,
        }


@pytest.mark.asyncio
async def test_login_flow_checker_attempts_login_with_credentials():
    tool = LoginFlowCheckerTool(computer_tool=_FakeComputer(), fallback_url="https://example.com/login")
    result = await tool.execute({"username": "user@example.com", "password": "secret"})

    assert result.success is True
    payload = json.loads(result.output or "{}")
    assert payload["attempted_login"] is True
    assert payload["login_result"]["likely_success"] is True
    assert payload["login_surface"]["password_input_count"] == 1
    codes = {item["code"] for item in payload["finding_details"]}
    assert "login_surface_detected" in codes
    assert "login_attempt_likely_successful" in codes
