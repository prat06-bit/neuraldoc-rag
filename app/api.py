"""FastAPI server — uses rag.pipeline.Pipeline as the single backend."""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.pipeline import Pipeline

app = FastAPI(
    title="Production RAG API",
    description="Domain-specific RAG with hybrid retrieval and attributed QA.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)

# --- Shared pipeline instance ---
pipe = Pipeline()


# --- Request / Response models ---

class QueryRequest(BaseModel):
    query: str
    k_final: int = 5


class QueryResponse(BaseModel):
    query: str
    answer: str
    references: list[str]
    refused: bool
    latency_ms: float


class ConfigUpdateRequest(BaseModel):
    provider: str | None = None
    ollama_model: str | None = None
    ollama_base_url: str | None = None
    openai_model: str | None = None
    temperature: float | None = None
    similarity_threshold: float | None = None


class IngestResponse(BaseModel):
    filename: str
    chunks_indexed: int
    total_chunks: int


# --- Endpoints ---

@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "pipeline_ready": pipe.is_ready,
        "indexed_files": pipe.indexed_files,
        "total_chunks": len(pipe.all_chunks),
    }


@app.get("/config")
def get_config() -> dict[str, Any]:
    cfg = pipe.cfg
    return {
        "provider": cfg.generation.provider,
        "ollama_model": cfg.generation.ollama_model,
        "ollama_base_url": cfg.generation.ollama_base_url,
        "openai_model": cfg.generation.openai_model,
        "temperature": cfg.generation.temperature,
        "embedding_model": cfg.retrieval.embedding_model,
        "similarity_threshold": cfg.retrieval.similarity_threshold,
        "k_final": cfg.retrieval.k_final,
    }


@app.post("/config/update")
def update_config(req: ConfigUpdateRequest) -> dict[str, Any]:
    gen = pipe.cfg.generation

    if req.provider is not None:
        gen.provider = req.provider
    if req.ollama_model is not None:
        gen.ollama_model = req.ollama_model
    if req.ollama_base_url is not None:
        gen.ollama_base_url = req.ollama_base_url
    if req.openai_model is not None:
        gen.openai_model = req.openai_model
    if req.temperature is not None:
        gen.temperature = req.temperature
    if req.similarity_threshold is not None:
        pipe.cfg.retrieval.similarity_threshold = req.similarity_threshold

    pipe.rebuild_graph()
    return {
        "message": "Config updated.",
        "current": {
            "provider": gen.provider,
            "model": gen.ollama_model if gen.provider == "ollama" else gen.openai_model,
        },
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)) -> IngestResponse:
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    save_path = UPLOAD_DIR / (file.filename or "upload.pdf")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        chunks = pipe.ingest(str(save_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IngestResponse(
        filename=file.filename or "upload.pdf",
        chunks_indexed=len(chunks),
        total_chunks=len(pipe.all_chunks),
    )


@app.delete("/index")
def clear_index() -> dict[str, str]:
    try:
        pipe.clear()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Also delete uploaded PDFs so reindex starts clean
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
        UPLOAD_DIR.mkdir(exist_ok=True)

    return {"message": "Index cleared. All chunks and uploaded files removed."}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    if not pipe.is_ready:
        raise HTTPException(
            status_code=400,
            detail="No documents indexed yet. POST a PDF to /ingest first.",
        )
    start = time.perf_counter()
    try:
        result = pipe.query(req.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    latency = (time.perf_counter() - start) * 1000

    return QueryResponse(
        query=req.query,
        answer=result["response"],
        references=result["references"],
        refused=result["refused"],
        latency_ms=round(latency, 1),
    )
