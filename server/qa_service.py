from __future__ import annotations

import asyncio
import base64
import binascii
import uuid
from pathlib import Path
from urllib.parse import urlparse

from fastapi import HTTPException

from engine import Engine, QATask
from server.schemas import QARequest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = PROJECT_ROOT / "artifacts" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise HTTPException(
            status_code=400, detail="Invalid URL. Provide a valid http/https URL."
        )
    return url


def run_qa_task_sync(task: QATask, request: QARequest):
    async def _runner():
        qa_engine = Engine(
            provider_name="mistral",
            model="mistral-large-latest",
            provider_kwargs=None,
            locale="en-US",
            device_profile=request.device_profile,
            network_profile=request.network_profile,
        )
        return await qa_engine.run_task(task)

    return asyncio.run(_runner())


def save_screenshot_base64(image_b64: str) -> str:
    try:
        image_bytes = base64.b64decode(image_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid screenshot base64 payload.") from exc

    filename = f"{uuid.uuid4().hex}.png"
    file_path = SCREENSHOT_DIR / filename
    file_path.write_bytes(image_bytes)
    return f"/screenshots/{filename}"


def serialize_tool_outputs_with_urls(tool_outputs, base_url: str):
    base = base_url.rstrip("/")
    serialized = []
    screenshot_urls = []
    for t in tool_outputs:
        item = dict(t.__dict__)
        image_b64 = item.get("screenshot_base64")
        if image_b64:
            screenshot_path = save_screenshot_base64(image_b64)
            screenshot_url = f"{base}{screenshot_path}"
            metadata = dict(item.get("metadata") or {})
            metadata["screenshot_url"] = screenshot_url
            item["metadata"] = metadata
            item["screenshot_base64"] = None
            screenshot_urls.append(screenshot_url)
        serialized.append(item)
    return serialized, screenshot_urls
