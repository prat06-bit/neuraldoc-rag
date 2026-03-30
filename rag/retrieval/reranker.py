from __future__ import annotations

import logging
from sentence_transformers import CrossEncoder
from rag.config import RetrievalConfig
from rag.exceptions import InsufficientEvidenceError
from rag.models import RetrievalResult

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    def __init__(self, config: RetrievalConfig | None = None) -> None:
        self._config = config or RetrievalConfig()
        self._model = CrossEncoder(
            self._config.cross_encoder_model,
            max_length=512,
        )

    def rerank(
        self,
        query: str,
        candidates: list[RetrievalResult],
        enforce_threshold: bool = True,
    ) -> list[RetrievalResult]:
        """Re-rank candidates and apply the similarity threshold gate.

        Args:
            query: The original user query.
            candidates: Pre-filtered candidates from the hybrid retriever.
            enforce_threshold: If True (default), raises InsufficientEvidenceError
                when the best score is below the configured threshold.

        Returns:
            Top-k_final candidates, sorted by cross-encoder score descending.

        Raises:
            InsufficientEvidenceError: If best score < similarity_threshold
                and enforce_threshold is True.
        """
        if not candidates:
            if enforce_threshold:
                raise InsufficientEvidenceError(
                    max_score=0.0,
                    threshold=self._config.similarity_threshold,
                    message="No candidates available for re-ranking.",
                )
            return []

        # Prepare (query, passage) pairs
        pairs = [(query, c.chunk.text) for c in candidates]

        # Score all pairs
        scores = self._model.predict(pairs)

        # Attach scores and sort
        scored_results = []
        for candidate, score in zip(candidates, scores):
            scored_results.append(
                RetrievalResult(
                    chunk=candidate.chunk,
                    score=float(score),
                    retriever_source="reranked",
                )
            )

        scored_results.sort(key=lambda r: r.score, reverse=True)

        # Enforce similarity threshold
        max_score = scored_results[0].score if scored_results else 0.0
        if enforce_threshold and max_score < self._config.similarity_threshold:
            raise InsufficientEvidenceError(
                max_score=max_score,
                threshold=self._config.similarity_threshold,
            )

        # Return top k_final
        k_final = self._config.k_final
        top_results = scored_results[:k_final]

        logger.info(
            "Re-ranked %d candidates -> top %d (max_score=%.4f, threshold=%.4f)",
            len(candidates),
            len(top_results),
            max_score,
            self._config.similarity_threshold,
        )

        return top_results
