"""
FastAPI backend for the Production RAG System.

Endpoints
---------
POST /query          — run a RAG query, returns answer + citations
POST /ingest         — upload and index a PDF
GET  /health         — health check
GET  /config         — show current config
POST /config/update  — update model/provider at runtime (upgrade path)

Start
-----
    uv add fastapi uvicorn python-multipart
    uv run uvicorn api:app --reload --port 8000
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.config import GenerationConfig, load_config
from rag.ingestion.chunker import Chunker
from rag.ingestion.pdf_parser import ParserFactory
from rag.retrieval.hybrid_retriever import HybridRetriever
from rag.retrieval.vector_store import VectorStore
from rag.generation.graph import RAGGraph
from rag.exceptions import InsufficientEvidenceError

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Global pipeline state (lazy init)
# ---------------------------------------------------------------------------

class PipelineState:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.store: VectorStore | None = None
        self.retriever: HybridRetriever | None = None
        self.graph: RAGGraph | None = None
        self.indexed_files: list[str] = []
        self.all_chunks: list = []

    def is_ready(self) -> bool:
        return self.graph is not None and self.retriever is not None

    def init_pipeline(self) -> None:
        self.store = VectorStore(self.cfg.retrieval)
        self.retriever = HybridRetriever(self.store, self.cfg.retrieval)
        self.graph = RAGGraph(self.cfg.generation, self.retriever)

    def rebuild_graph(self) -> None:
        """Rebuild only the graph (after config change)."""
        if self.retriever:
            self.graph = RAGGraph(self.cfg.generation, self.retriever)

    def ingest_pdf(self, pdf_path: str) -> int:
        """Parse, chunk and index a PDF. Returns chunk count."""
        if self.store is None or self.retriever is None:
            self.init_pipeline()

        parser = ParserFactory.create(
            self.cfg.ingestion.parser_strategy, self.cfg.ingestion
        )
        doc = parser.parse(pdf_path)
        chunks = Chunker(self.cfg.chunking).chunk(doc)

        self.store.add_chunks(chunks)  # type: ignore[union-attr]
        self.all_chunks.extend(chunks)
        self.retriever.build_bm25(self.all_chunks)  # type: ignore[union-attr]

        if self.graph is None:
            self.graph = RAGGraph(self.cfg.generation, self.retriever)

        self.indexed_files.append(pdf_path)
        return len(chunks)


state = PipelineState()

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

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
    provider: str | None = None          # "ollama" or "openai"
    ollama_model: str | None = None      # e.g. "llama3.3:70b"
    ollama_base_url: str | None = None
    openai_model: str | None = None      # e.g. "gpt-4o"
    temperature: float | None = None
    similarity_threshold: float | None = None


class IngestResponse(BaseModel):
    filename: str
    chunks_indexed: int
    total_chunks: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "pipeline_ready": state.is_ready(),
        "indexed_files": state.indexed_files,
        "total_chunks": len(state.all_chunks),
    }


@app.get("/config")
def get_config() -> dict[str, Any]:
    cfg = state.cfg
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
    """
    Hot-swap model or provider at runtime — no restart needed.

    Example — upgrade to 70B judge:
        POST /config/update
        {"provider": "ollama", "ollama_model": "llama3.3:70b"}

    Example — switch to OpenAI:
        POST /config/update
        {"provider": "openai", "openai_model": "gpt-4o"}
    """
    gen = state.cfg.generation

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
        state.cfg.retrieval.similarity_threshold = req.similarity_threshold

    # Rebuild graph with new config
    state.rebuild_graph()

    return {
        "message": "Config updated. Graph rebuilt with new settings.",
        "current": {
            "provider": gen.provider,
            "model": gen.ollama_model if gen.provider == "ollama" else gen.openai_model,
        },
    }


@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: UploadFile = File(...)) -> IngestResponse:
    """Upload and index a PDF file."""
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    save_path = UPLOAD_DIR / (file.filename or "upload.pdf")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        count = state.ingest_pdf(str(save_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return IngestResponse(
        filename=file.filename or "upload.pdf",
        chunks_indexed=count,
        total_chunks=len(state.all_chunks),
    )


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    """Run a RAG query against all indexed documents."""
    if not state.is_ready():
        raise HTTPException(
            status_code=400,
            detail="No documents indexed yet. POST a PDF to /ingest first.",
        )

    start = time.perf_counter()
    try:
        result = state.graph.run(req.query)  # type: ignore[union-attr]
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
