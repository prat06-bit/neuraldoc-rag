from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from rag.config import EvaluationConfig, RAGConfig
from rag.evaluation.gatekeeper import CIGatekeeper
from rag.models import EvaluationResult


def _write_golden_dataset(samples: list[dict[str, Any]]) -> Path:
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(samples, tmp)
    tmp.close()
    return Path(tmp.name)


def _sample_dataset() -> list[dict[str, Any]]:
    return [
        {
            "question": "What is the dosage?",
            "ground_truth_answer": "500mg daily.",
            "expected_citations": [
                {"source_file": "guide.pdf", "page_number": 10}
            ],
        }
    ]


class TestCIGatekeeper:
    def test_passes_when_faithfulness_above_threshold_and_citations_present(
        self,
    ) -> None:
        """Gatekeeper should pass with high faithfulness and matching citations."""
        config = RAGConfig(
            evaluation=EvaluationConfig(faithfulness_threshold=0.85)
        )

        # Mock pipeline that returns an answer containing the expected citation
        pipeline = MagicMock(
            return_value={
                "answer": "The dosage is 500mg [guide, p. 10].",
                "citations": [{"source_file": "guide.pdf", "page_number": 10}],
                "contexts": ["The dosage is 500mg daily."],
            }
        )

        # Mock evaluator returning high faithfulness
        evaluator = MagicMock()
        evaluator.evaluate.return_value = EvaluationResult(
            context_precision=0.95,
            faithfulness=0.92,
            answer_relevancy=0.90,
        )

        dataset_path = _write_golden_dataset(_sample_dataset())
        gatekeeper = CIGatekeeper(
            config=config, rag_pipeline=pipeline, evaluator=evaluator
        )
        result = gatekeeper.run(dataset_path)

        assert result.passed is True
        assert result.exit_code == 0
        assert result.faithfulness_score >= 0.85

    def test_fails_when_faithfulness_below_threshold(self) -> None:
        """Gatekeeper should fail with exit_code=1 when faithfulness is low."""
        config = RAGConfig(
            evaluation=EvaluationConfig(faithfulness_threshold=0.85)
        )

        pipeline = MagicMock(
            return_value={
                "answer": "The dosage is 500mg [guide, p. 10].",
                "citations": [],
                "contexts": [],
            }
        )

        evaluator = MagicMock()
        evaluator.evaluate.return_value = EvaluationResult(
            context_precision=0.50,
            faithfulness=0.60,  # Below 0.85 threshold
            answer_relevancy=0.70,
        )

        dataset_path = _write_golden_dataset(_sample_dataset())
        gatekeeper = CIGatekeeper(
            config=config, rag_pipeline=pipeline, evaluator=evaluator
        )
        result = gatekeeper.run(dataset_path)

        assert result.passed is False
        assert result.exit_code == 1

    def test_fails_when_expected_citations_missing(self) -> None:
        """Gatekeeper should fail when expected citations are not in the answer."""
        config = RAGConfig(
            evaluation=EvaluationConfig(faithfulness_threshold=0.85)
        )

        # Pipeline answer does NOT contain the expected citation
        pipeline = MagicMock(
            return_value={
                "answer": "The dosage is 500mg daily.",
                "citations": [],
                "contexts": ["The dosage is 500mg daily."],
            }
        )

        evaluator = MagicMock()
        evaluator.evaluate.return_value = EvaluationResult(
            context_precision=0.95,
            faithfulness=0.92,
            answer_relevancy=0.90,
        )

        dataset_path = _write_golden_dataset(_sample_dataset())
        gatekeeper = CIGatekeeper(
            config=config, rag_pipeline=pipeline, evaluator=evaluator
        )
        result = gatekeeper.run(dataset_path)

        assert result.passed is False
        assert result.exit_code == 1
        assert len(result.missing_citations) > 0
        assert result.missing_citations[0]["expected_source"] == "guide.pdf"

    def test_reports_faithfulness_score(self) -> None:
        """Result should always contain the faithfulness score."""
        config = RAGConfig()
        pipeline = MagicMock(
            return_value={"answer": "", "citations": [], "contexts": []}
        )
        evaluator = MagicMock()
        evaluator.evaluate.return_value = EvaluationResult(
            context_precision=0.0, faithfulness=0.42, answer_relevancy=0.0
        )

        dataset_path = _write_golden_dataset(_sample_dataset())
        gatekeeper = CIGatekeeper(
            config=config, rag_pipeline=pipeline, evaluator=evaluator
        )
        result = gatekeeper.run(dataset_path)

        assert result.faithfulness_score == 0.42

    def test_invalid_dataset_raises_error(self) -> None:
        """Loading an invalid dataset should raise ValueError."""
        bad_data = [{"question": "no other keys"}]
        dataset_path = _write_golden_dataset(bad_data)
        gatekeeper = CIGatekeeper()

        try:
            gatekeeper.run(dataset_path)
            assert False, "Should have raised ValueError"
        except ValueError as exc:
            assert "missing required keys" in str(exc).lower()
