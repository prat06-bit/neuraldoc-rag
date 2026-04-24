from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from rag.config import RetrievalConfig
from rag.models import ChunkMetadata, DocumentChunk

import os
import tempfile

@dataclass
class ScoredChunk:
    chunk: DocumentChunk
    score: float

def _default_persist_dir() -> str:
    """Use /tmp on Streamlit Cloud (read-only filesystem), local dir otherwise."""
    if os.environ.get("STREAMLIT_SERVER_HEADLESS") or os.path.exists("/mount"):
        return os.path.join(tempfile.gettempdir(), "neuraldoc_chroma_db")
    return "chroma_db"

class VectorStore:
    def __init__(self, config: RetrievalConfig, persist_dir: str | Path | None = None, collection: str = "rag_chunks") -> None:
        self.config = config
        self.persist_dir = str(Path(persist_dir or _default_persist_dir()).resolve())
        self.collection_name = collection
        self._client = None
        self._collection = None
        self._embedder = None

    def _get_client(self):
        if self._client is None:
            import chromadb
            self._client = chromadb.PersistentClient(path=self.persist_dir)
        return self._client

    def _get_collection(self):
        if self._collection is None:
            self._collection = self._get_client().get_or_create_collection(name=self.collection_name, metadata={"hnsw:space": "cosine"})
        return self._collection

    def _get_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(self.config.embedding_model)
        return self._embedder

    def add_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return
        embedder = self._get_embedder()
        collection = self._get_collection()
        texts = [c.text for c in chunks]
        ids = [c.chunk_id for c in chunks]
        metadatas = [self._serialise_metadata(c) for c in chunks]
        print(f"Embedding {len(texts)} chunks...")
        embeddings = embedder.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True).tolist()
        collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
        print(f"Upserted {len(ids)} chunks.")

    def similarity_search(self, query: str, k: int | None = None) -> list[ScoredChunk]:
        top_k = k or self.config.k_initial
        embedder = self._get_embedder()
        collection = self._get_collection()
        query_embedding = embedder.encode([query], convert_to_numpy=True).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=min(top_k, collection.count()), include=["documents", "metadatas", "distances"])
        scored: list[ScoredChunk] = []
        for text, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            scored.append(ScoredChunk(chunk=self._deserialise_chunk(text, meta), score=1.0 - float(dist) / 2.0))
        return sorted(scored, key=lambda x: x.score, reverse=True)

    def count(self) -> int:
        return self._get_collection().count()

    def clear(self) -> None:
        self._get_client().delete_collection(self.collection_name)
        self._collection = None

    @staticmethod
    def _serialise_metadata(chunk: DocumentChunk) -> dict[str, Any]:
        return {"chunk_id": chunk.chunk_id, "source": chunk.metadata.source, "page": chunk.metadata.page, "token_count": chunk.token_count, "breadcrumb_path": json.dumps(chunk.metadata.breadcrumb_path)}

    @staticmethod
    def _deserialise_chunk(text: str, meta: dict[str, Any]) -> DocumentChunk:
        return DocumentChunk(chunk_id=str(meta.get("chunk_id", "")), text=text, token_count=int(meta.get("token_count", 1)), metadata=ChunkMetadata(source=str(meta.get("source", "")), page=int(meta.get("page", 1)), breadcrumb_path=json.loads(meta.get("breadcrumb_path", "[]"))))
