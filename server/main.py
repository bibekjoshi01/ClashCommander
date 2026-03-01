from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from engine import Engine, QATask

DEFAULT_TASK = "Explore the main user flow and report functional, UX, and accessibility issues."

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


class QARequest(BaseModel):
    url: str = Field(..., description="Website URL to test")
    task: Optional[str] = Field(
        default=None,
        description="Optional QA objective. Uses engine default if not provided.",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context for QA flow (credentials, test notes, etc.)",
    )
    provider_name: str = Field(default="mistral", description="LLM provider name")
    model: str = Field(default="mistral-large-latest", description="Model name")
    max_iterations: int = Field(default=20, ge=1, le=100)
    locale: str = Field(default="en-US")
    persona: Optional[str] = Field(default=None)
    device_profile: str = Field(default="iphone_14")
    network_profile: str = Field(default="wifi")
    provider_kwargs: Optional[Dict[str, Any]] = Field(default=None)


class QAResponse(BaseModel):
    url: str
    issues: List[Dict[str, Any]]
    tool_outputs: List[Dict[str, Any]]
    screenshots: List[str]
    raw_model_output: Optional[str]
    trace: List[Dict[str, Any]]


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL. Provide a valid http/https URL.")
    return url


@app.post("/api/qa", response_model=QAResponse)
@app.post("/qa", response_model=QAResponse)  # Backward-compatible route
async def qa_endpoint(request: QARequest):
    target_url = _normalize_url(request.url)
    task = QATask(
        target_url=target_url,
        task=request.task or DEFAULT_TASK,
        context=request.context,
    )

    try:
        qa_engine = Engine(
            provider_name=request.provider_name,
            model=request.model,
            provider_kwargs=request.provider_kwargs,
            max_iterations=request.max_iterations,
            locale=request.locale,
            persona=request.persona,
            device_profile=request.device_profile,
            network_profile=request.network_profile,
        )
        result = await qa_engine.run_task(task)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"QA run failed: {exc}") from exc

    return {
        "url": target_url,
        "issues": result.issues,
        "tool_outputs": [t.__dict__ for t in result.tool_outputs],
        "screenshots": result.screenshots,
        "raw_model_output": result.raw_model_output,
        "trace": result.trace,
    }
