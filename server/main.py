from fastapi import FastAPI
from pydantic import BaseModel
from engine import run_qa_engine

app = FastAPI()


@app("/health")
def health():
    return {"status": "ok"}


app = FastAPI()


class QARequest(BaseModel):
    url: str


@app.post("/qa")
async def qa_endpoint(request: QARequest):
    result = await run_qa_engine(request.url)
    return {
        "issues": result.issues,
        "tool_outputs": [t.__dict__ for t in result.tool_outputs],
        "screenshots": result.screenshots,
        "raw_model_output": result.raw_model_output,
    }
