from __future__ import annotations

from pathlib import Path
from typing import Any

from rag.config import RAGConfig, load_config
from rag.ingestion.chunker import Chunker
from rag.ingestion.pdf_parser import ParserFactory
from rag.models import DocumentChunk
from rag.retrieval.hybrid_retriever import HybridRetriever
from rag.retrieval.vector_store import VectorStore


class Pipeline:
    def __init__(self, cfg: RAGConfig | None = None) -> None:
        self.cfg = cfg or load_config()
        self.store = VectorStore(self.cfg.retrieval)
        self.retriever = HybridRetriever(self.store, self.cfg.retrieval)
        self._graph = None          # lazy — built on first query
        self.all_chunks: list[DocumentChunk] = []
        self.indexed_files: list[str] = []

    # Queries
    @property
    def is_ready(self) -> bool:
        return len(self.all_chunks) > 0

    @property
    def graph(self):
        """Lazy-build the generation graph on first access."""
        if self._graph is None:
            from rag.generation.graph import RAGGraph
            self._graph = RAGGraph(self.cfg.generation, self.retriever)
        return self._graph

    def query(self, question: str) -> dict[str, Any]:
        """Run a RAG query end-to-end.  Returns the graph output dict."""
        return self.graph.run(question)

    # Ingestion

    def ingest(self, pdf_path: str | Path) -> list[DocumentChunk]:
        pdf_path = str(pdf_path)
        parser = ParserFactory.create(
            self.cfg.ingestion.parser_strategy, self.cfg.ingestion
        )
        doc = parser.parse(pdf_path)
        chunks = Chunker(self.cfg.chunking).chunk(doc)

        self.store.add_chunks(chunks)
        self.all_chunks.extend(chunks)
        self.retriever.build_bm25(self.all_chunks)

        self._graph = None
        self.indexed_files.append(pdf_path)
        return chunks

    # Lifecycle

    def clear(self) -> None:
        self.store.clear()
        self.store = VectorStore(self.cfg.retrieval)
        self.retriever = HybridRetriever(self.store, self.cfg.retrieval)
        self._graph = None
        self.all_chunks = []
        self.indexed_files = []

    def rebuild_graph(self) -> None:
        from rag.generation.graph import RAGGraph
        self._graph = RAGGraph(self.cfg.generation, self.retriever)
