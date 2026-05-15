from fastapi import FastAPI
from uuid import UUID
from typing import Any

app = FastAPI()


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}
