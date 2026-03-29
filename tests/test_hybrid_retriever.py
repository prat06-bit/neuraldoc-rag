from __future__ import annotations

from rag.config import RetrievalConfig
from rag.models import Chunk, RetrievalResult
from rag.retrieval.hybrid_retriever import HybridRetriever


def _make_chunk(chunk_id: str, text: str = "sample text") -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        text=text,
        source_file="test.pdf",
        page_number=1,
        breadcrumb_path="Test > Section",
        token_count=5,
    )


def _make_result(
    chunk_id: str, score: float, source: str = "bm25"
) -> RetrievalResult:
    return RetrievalResult(
        chunk=_make_chunk(chunk_id),
        score=score,
        retriever_source=source,
    )


class TestRRFFusion:
    """Tests for the RRF fusion logic in HybridRetriever."""

    def setup_method(self) -> None:
        self.config = RetrievalConfig(
            alpha=0.5, rrf_k=60, k_initial=10, k_final=3
        )

    def test_rrf_combines_both_sources(self) -> None:
        """RRF fusion should include chunks from both retrievers."""
        bm25_results = [
            _make_result("a", 10.0, "bm25"),
            _make_result("b", 8.0, "bm25"),
        ]
        vector_results = [
            _make_result("b", 0.9, "vector"),
            _make_result("c", 0.8, "vector"),
        ]

        retriever = HybridRetriever.__new__(HybridRetriever)
        retriever._config = self.config

        fused = retriever._rrf_fusion(bm25_results, vector_results)
        fused_ids = {r.chunk.chunk_id for r in fused}

        assert "a" in fused_ids
        assert "b" in fused_ids
        assert "c" in fused_ids

    def test_rrf_boosts_overlapping_chunks(self) -> None:
        """Chunks appearing in both result sets should have higher scores."""
        bm25_results = [
            _make_result("shared", 10.0, "bm25"),
            _make_result("bm25_only", 8.0, "bm25"),
        ]
        vector_results = [
            _make_result("shared", 0.9, "vector"),
            _make_result("vec_only", 0.8, "vector"),
        ]

        retriever = HybridRetriever.__new__(HybridRetriever)
        retriever._config = self.config

        fused = retriever._rrf_fusion(bm25_results, vector_results)
        score_map = {r.chunk.chunk_id: r.score for r in fused}

        # "shared" should score higher than single-source chunks
        assert score_map["shared"] > score_map["bm25_only"]
        assert score_map["shared"] > score_map["vec_only"]

    def test_alpha_1_favors_bm25(self) -> None:
        """With alpha=1.0, BM25-only chunks should score and vector-only should not."""
        config = RetrievalConfig(alpha=1.0, rrf_k=60, k_initial=10)
        bm25_results = [_make_result("bm25_chunk", 10.0, "bm25")]
        vector_results = [_make_result("vec_chunk", 0.9, "vector")]

        retriever = HybridRetriever.__new__(HybridRetriever)
        retriever._config = config

        fused = retriever._rrf_fusion(bm25_results, vector_results)
        score_map = {r.chunk.chunk_id: r.score for r in fused}

        # With alpha=1.0, vector contribution is 0
        assert score_map["bm25_chunk"] > 0
        assert score_map["vec_chunk"] == 0.0

    def test_alpha_0_favors_vector(self) -> None:
        """With alpha=0.0, vector-only chunks should score and BM25 should not."""
        config = RetrievalConfig(alpha=0.0, rrf_k=60, k_initial=10)
        bm25_results = [_make_result("bm25_chunk", 10.0, "bm25")]
        vector_results = [_make_result("vec_chunk", 0.9, "vector")]

        retriever = HybridRetriever.__new__(HybridRetriever)
        retriever._config = config

        fused = retriever._rrf_fusion(bm25_results, vector_results)
        score_map = {r.chunk.chunk_id: r.score for r in fused}

        assert score_map["vec_chunk"] > 0
        assert score_map["bm25_chunk"] == 0.0

    def test_fused_results_tagged_as_ensemble(self) -> None:
        """All fused results should have retriever_source='ensemble'."""
        bm25_results = [_make_result("a", 10.0, "bm25")]
        vector_results = [_make_result("b", 0.9, "vector")]

        retriever = HybridRetriever.__new__(HybridRetriever)
        retriever._config = self.config

        fused = retriever._rrf_fusion(bm25_results, vector_results)
        for result in fused:
            assert result.retriever_source == "ensemble"

    def test_empty_inputs_produce_empty_fusion(self) -> None:
        """RRF with empty inputs should return empty results."""
        retriever = HybridRetriever.__new__(HybridRetriever)
        retriever._config = self.config

        fused = retriever._rrf_fusion([], [])
        assert fused == []
