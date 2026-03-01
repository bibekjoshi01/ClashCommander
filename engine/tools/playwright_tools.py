from playwright.async_api import Page
from .base import BaseTool
from .base import ToolExecutionResult


class ClickTool(BaseTool):
    name = "click"
    description = "Click an element by CSS selector"

    def __init__(self, page: Page):
        self.page = page

    async def execute(self, arguments):
        selector = arguments.get("selector")
        try:
            await self.page.click(selector)
            return ToolExecutionResult(output=f"Clicked {selector}")
        except Exception as e:
            return ToolExecutionResult(error=str(e))
