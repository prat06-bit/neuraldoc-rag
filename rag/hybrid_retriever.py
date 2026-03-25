from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from rag.config import RetrievalConfig
from rag.models import DocumentChunk
from rag.retrieval.vector_store import ScoredChunk, VectorStore

class BM25Retriever:
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self.chunks = chunks
        self._bm25 = None
        self._build(chunks)

    def _build(self, chunks: list[DocumentChunk]) -> None:
        try:
            from rank_bm25 import BM25Okapi  
        except ImportError as exc:
            raise ImportError(
                "rank-bm25 is required. Install with: uv add rank-bm25"
            ) from exc

        tokenised = [doc.text.lower().split() for doc in chunks]
        self._bm25 = BM25Okapi(tokenised)

    def search(self, query: str, k: int) -> list[ScoredChunk]:
        if self._bm25 is None or not self.chunks:
            return []

        tokens = query.lower().split()
        scores: list[float] = self._bm25.get_scores(tokens).tolist()

        # Pair each chunk with its BM25 score sortin descending order
        paired = sorted(
            zip(self.chunks, scores),
            key=lambda x: x[1],
            reverse=True,
        )
        return [
            ScoredChunk(chunk=chunk, score=float(score))
            for chunk, score in paired[:k]
        ]

# RRF Fusion

def reciprocal_rank_fusion(
    ranked_lists: list[list[ScoredChunk]],
    k: int = 60,
) -> list[ScoredChunk]:
    rrf_scores: dict[str, float] = {}
    chunk_index: dict[str, DocumentChunk] = {}

    for ranked in ranked_lists:
        for rank, scored in enumerate(ranked, start=1):
            cid = scored.chunk.chunk_id
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k + rank)
            chunk_index[cid] = scored.chunk

    fused = [
        ScoredChunk(chunk=chunk_index[cid], score=rrf_scores[cid])
        for cid in sorted(rrf_scores, key=lambda x: rrf_scores[x], reverse=True)
    ]
    return fused

# Cross-Encoder Re-ranker

class CrossEncoderReranker:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    def _get_model(self): 
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder  
            except ImportError as exc:
                raise ImportError(
                    "sentence-transformers is required. "
                    "Install with: uv add sentence-transformers"
                ) from exc
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(
        self,
        query: str,
        candidates: list[ScoredChunk],
        k: int,
    ) -> list[ScoredChunk]:
        if not candidates:
            return []

        model = self._get_model()
        pairs = [[query, sc.chunk.text] for sc in candidates]
        scores: list[float] = model.predict(pairs).tolist()

        reranked = sorted(
            [
                ScoredChunk(chunk=sc.chunk, score=float(s))
                for sc, s in zip(candidates, scores)
            ],
            key=lambda x: x.score,
            reverse=True,
        )
        return reranked[:k]

# Hybrid Retriever

class HybridRetriever:
    def __init__(
        self,
        vector_store: VectorStore,
        config: RetrievalConfig,
    ) -> None:
        self.vector_store = vector_store
        self.config = config
        self._bm25: BM25Retriever | None = None
        self._reranker = CrossEncoderReranker(config.cross_encoder_model)

    def build_bm25(self, chunks: list[DocumentChunk]) -> None:
        """Index chunks into the in-memory BM25 retriever."""
        self._bm25 = BM25Retriever(chunks)
        print(f"BM25 index built over {len(chunks)} chunks.")

    def retrieve(
        self,
        query: str,
        k_final: int | None = None,
    ) -> list[ScoredChunk]:
        k_init = self.config.k_initial
        k_out = k_final or self.config.k_final

        # Step 1: BM25 
        bm25_results: list[ScoredChunk] = []
        if self._bm25 is not None:
            bm25_results = self._bm25.search(query, k=k_init)

        # --- Step 2: Vector ---
        vector_results = self.vector_store.similarity_search(query, k=k_init)

        # --- Step 3: RRF Fusion ---
        fused = reciprocal_rank_fusion(
            [bm25_results, vector_results],
            k=self.config.rrf_k,
        )

        # --- Step 4: Re-rank ---
        reranked = self._reranker.rerank(query, fused[:k_init], k=k_out)

        # --- Step 5: Threshold check ---
        if reranked:
            best_score = reranked[0].score
            if best_score < self.config.similarity_threshold:
                from rag.exceptions import InsufficientEvidenceError
                raise InsufficientEvidenceError(
                    max_score=best_score,
                    threshold=self.config.similarity_threshold,
                )

        return reranked
