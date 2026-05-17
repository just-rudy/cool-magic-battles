from typing import Any

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}
