from __future__ import annotations

from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException

from engine import Engine, QATask
from server.schemas import QARequest, QAResponse

DEFAULT_TASK = (
    "Explore the main user flow and report functional, UX, and accessibility issues."
)

app = FastAPI()


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(
            status_code=400, detail="Invalid URL. Provide a valid http/https URL."
        )
    return url


@app.post("/api/qa", response_model=QAResponse)
async def qa_endpoint(request: QARequest):
    target_url = _normalize_url(request.url)
    task = QATask(
        target_url=target_url,
        task=DEFAULT_TASK,
        context=request.context,
    )

    try:
        qa_engine = Engine(
            provider_name="huggingface",
            model="mistralai/Mistral-7B-Instruct-v0.3",
            provider_kwargs=None,
            locale="en-US",
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
