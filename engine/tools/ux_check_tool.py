from playwright.async_api import Page
from .base import BaseTool, ToolExecutionResult


class UXCheckTool(BaseTool):
    name = "ux_check"
    description = "Perform basic UX checks on a page."

    async def execute(self, input_data: dict):
        page: Page = input_data["page"]
        issues = []

        # Tiny buttons (<44x44px)
        buttons = await page.query_selector_all("button,a")
        for btn in buttons:
            bounding = await btn.bounding_box()
            if bounding and (bounding["width"] < 44 or bounding["height"] < 44):
                issues.append(
                    f"Tiny touch target: {await btn.evaluate('e => e.outerHTML')}"
                )

        # Overlapping elements (simple check: compare bounding boxes)
        elems = await page.query_selector_all("*")
        for i in range(len(elems)):
            box1 = await elems[i].bounding_box()
            if not box1:
                continue
            for j in range(i + 1, len(elems)):
                box2 = await elems[j].bounding_box()
                if not box2:
                    continue
                if (
                    box1["x"] < box2["x"] + box2["width"]
                    and box1["x"] + box1["width"] > box2["x"]
                    and box1["y"] < box2["y"] + box2["height"]
                    and box1["y"] + box1["height"] > box2["y"]
                ):
                    issues.append("Potential overlapping elements detected")

        return ToolExecutionResult(success=True, output={"issues": issues})
