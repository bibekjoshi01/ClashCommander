import base64
from playwright.async_api import async_playwright
from .base import Tool, ToolExecutionResult


class BrowserTool(Tool):
    name = "browser_action"
    description = "Perform browser automation using Playwright."

    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "selector": {"type": "string"},
            "text": {"type": "string"},
            "url": {"type": "string"},
        },
        "required": ["action"],
    }

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._page = None

    async def _ensure_browser(self):
        if self._page:
            return

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._page = await self._browser.new_page()

    async def execute(self, input_data: dict):
        await self._ensure_browser()

        action = input_data["action"]

        try:
            if action == "goto":
                await self._page.goto(input_data["url"])

            elif action == "click":
                await self._page.click(input_data["selector"])

            elif action == "type":
                await self._page.fill(input_data["selector"], input_data["text"])

            elif action == "screenshot":
                png = await self._page.screenshot()
                b64 = base64.b64encode(png).decode()
                return ToolExecutionResult(
                    success=True,
                    screenshot_base64=b64,
                )

            return ToolExecutionResult(success=True)

        except Exception as e:
            return ToolExecutionResult(success=False, error=str(e))
