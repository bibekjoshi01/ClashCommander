from fastapi import FastAPI

app = FastAPI()


@app("/health")
def health():
    return {"status": "ok"}
