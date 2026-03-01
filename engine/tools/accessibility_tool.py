from playwright.async_api import Page
from .base import BaseTool, ToolExecutionResult


class AccessibilityTool(BaseTool):
    name = "accessibility_check"
    description = "Run basic accessibility checks on a page."

    async def execute(self, input_data: dict):
        page: Page = input_data["page"]  # must receive Page object
        issues = []

        # Small font detection
        elements = await page.query_selector_all("*")
        for el in elements:
            font_size = await el.evaluate(
                "e => parseFloat(window.getComputedStyle(e).fontSize)"
            )
            if font_size < 14:
                issues.append(
                    f"Font too small: {await el.evaluate('e => e.outerHTML')}"
                )

        # Missing alt attributes
        images = await page.query_selector_all("img")
        for img in images:
            alt = await img.get_attribute("alt")
            if not alt:
                issues.append(
                    f"Image missing alt text: {await img.evaluate('e => e.outerHTML')}"
                )

        # Low contrast simplified: gray text on black background
        for el in elements:
            color = await el.evaluate("e => window.getComputedStyle(e).color")
            bg = await el.evaluate("e => window.getComputedStyle(e).backgroundColor")
            if color == "rgb(169, 169, 169)" and bg == "rgb(0, 0, 0)":
                issues.append(f"Low contrast: {await el.evaluate('e => e.outerHTML')}")

        return ToolExecutionResult(success=True, output={"issues": issues})
