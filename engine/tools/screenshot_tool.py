import base64
from playwright.async_api import Page
from .base import BaseTool, ToolExecutionResult


class ScreenshotTool(BaseTool):
    name = "screenshot"
    description = "Take a full-page screenshot."

    async def execute(self, input_data: dict):
        page: Page = input_data["page"]
        img_bytes = await page.screenshot(full_page=True)
        b64 = base64.b64encode(img_bytes).decode()
        return ToolExecutionResult(success=True, screenshot_base64=b64)
