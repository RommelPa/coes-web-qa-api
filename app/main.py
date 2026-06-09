from __future__ import annotations

import os
import time
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from app.qa import DEFAULT_INDEX_PATH, WebQASystem, load_qa_system
from app.schemas import AskRequest, AskResponse, MetadataResponse


START_TIME = time.monotonic()
QUESTIONS_TOTAL = 0


app = FastAPI(
    title="COES Web QA API",
    description="Question-answering API over COES WebApi Mediciones documentation.",
    version="0.1.0",
)


@lru_cache
def get_qa_system() -> WebQASystem:
    index_path = Path(os.getenv("COES_INDEX_PATH", str(DEFAULT_INDEX_PATH)))
    return load_qa_system(index_path)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "COES Web QA API is running",
        "docs": "/docs",
        "health": "/health",
        "ask": "/ask",
        "metadata": "/metadata",
        "metrics": "/metrics",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metadata", response_model=MetadataResponse)
def metadata() -> MetadataResponse:
    try:
        qa_system = get_qa_system()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="QA index not found. Build data/index.json first.",
        ) from exc

    return MetadataResponse(**qa_system.metadata)


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    global QUESTIONS_TOTAL

    try:
        qa_system = get_qa_system()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="QA index not found. Build data/index.json first.",
        ) from exc

    QUESTIONS_TOTAL += 1
    result = qa_system.ask(question=payload.question, top_k=payload.top_k)

    return AskResponse(**result)


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    try:
        chunks_indexed = len(get_qa_system().chunks)
    except FileNotFoundError:
        chunks_indexed = 0

    uptime_seconds = time.monotonic() - START_TIME

    return "\n".join(
        [
            "# HELP coes_web_qa_uptime_seconds Application uptime in seconds.",
            "# TYPE coes_web_qa_uptime_seconds gauge",
            f"coes_web_qa_uptime_seconds {uptime_seconds:.2f}",
            "# HELP coes_web_qa_questions_total Total questions received.",
            "# TYPE coes_web_qa_questions_total counter",
            f"coes_web_qa_questions_total {QUESTIONS_TOTAL}",
            "# HELP coes_web_qa_chunks_indexed Total indexed chunks.",
            "# TYPE coes_web_qa_chunks_indexed gauge",
            f"coes_web_qa_chunks_indexed {chunks_indexed}",
            "",
        ]
    )