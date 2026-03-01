from __future__ import annotations

import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from engine import QATask
from server.qa_service import (
    SCREENSHOT_DIR,
    normalize_url,
    run_qa_task_sync,
    serialize_tool_outputs_with_urls,
)
from server.schemas import QARequest, QAResponse

DEFAULT_TASK = (
    "Explore the main user flow and report functional, UX, and accessibility issues."
)

app = FastAPI()
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOT_DIR)), name="screenshots")


@app.post("/api/qa", response_model=QAResponse)
async def qa_endpoint(request: QARequest, _http_request: Request):
    target_url = normalize_url(request.url)
    task = QATask(
        target_url=target_url,
        task=DEFAULT_TASK,
        context=request.context,
    )

    try:
        result = await asyncio.to_thread(run_qa_task_sync, task, request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QA run failed: {exc}") from exc

    tool_outputs, screenshot_urls = serialize_tool_outputs_with_urls(
        result.tool_outputs, str(_http_request.base_url)
    )
    return {
        "url": target_url,
        "issues": result.issues,
        "tool_outputs": tool_outputs,
        "screenshots": screenshot_urls,
        "raw_model_output": result.raw_model_output,
        "trace": result.trace,
    }
