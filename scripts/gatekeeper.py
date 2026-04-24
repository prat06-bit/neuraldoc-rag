from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rag.pipeline import Pipeline
from rag.evaluation.ragas_evaluator import RAGASEvaluator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RAG quality gate for CI.")
    parser.add_argument(
        "--dataset",
        default="tests/fixtures/golden_dataset.json",
        help="Path to golden dataset JSON file.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Minimum faithfulness score to pass (default: 0.85).",
    )
    parser.add_argument(
        "--pdf",
        default="tests/fixtures/sample.pdf",
        help="PDF to index for evaluation.",
    )
    return parser.parse_args()


def load_golden_dataset(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        print(f"[ERROR] Golden dataset not found: {path}")
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def run_evaluation(
    pipe: Pipeline,
    evaluator: RAGASEvaluator,
    dataset: list[dict],
    threshold: float,
) -> tuple[bool, list[dict]]:
    results: list[dict] = []
    all_passed = True

    for i, entry in enumerate(dataset, start=1):
        query: str = entry["query"]
        ground_truth: str = entry.get("ground_truth", "")
        expected_citations: list[str] = entry.get("expected_citations", [])

        print(f"\n[{i}/{len(dataset)}] Query: {query}")

        # Run RAG
        rag_result = pipe.query(query)
        answer: str = rag_result["response"]
        retrieved = rag_result.get("retrieved", [])
        contexts = [sc.chunk.text for sc in retrieved]

        print(f"  Answer: {answer[:120]}...")

        # Handle expected refusal
        if ground_truth == "INSUFFICIENT_EVIDENCE":
            refused = rag_result.get("refused", False) or (
                "does not contain sufficient evidence" in answer.lower()
            )
            status = "PASS" if refused else "FAIL"
            if not refused:
                all_passed = False
            print(f"  Refusal check: {status}")
            results.append({
                "query": query,
                "status": status,
                "refused_correctly": refused,
            })
            continue

        # Evaluate
        eval_result = evaluator.evaluate(
            query=query,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth,
        )

        # Citation check
        citations_ok = True
        if expected_citations:
            answer_lower = answer.lower()
            citations_ok = all(
                cite.lower() in answer_lower for cite in expected_citations
            )

        passed = eval_result.faithfulness >= threshold and citations_ok
        if not passed:
            all_passed = False

        status = "PASS" if passed else "FAIL"
        print(f"  Faithfulness  : {eval_result.faithfulness:.3f}  (threshold={threshold})")
        print(f"  Ctx Precision : {eval_result.context_precision:.3f}")
        print(f"  Ans Relevancy : {eval_result.answer_relevancy:.3f}")
        print(f"  Citations OK  : {citations_ok}")
        print(f"  Status        : {status}")

        results.append({
            "query": query,
            "status": status,
            "faithfulness": eval_result.faithfulness,
            "context_precision": eval_result.context_precision,
            "answer_relevancy": eval_result.answer_relevancy,
            "citations_ok": citations_ok,
        })

    return all_passed, results


def print_summary(results: list[dict], all_passed: bool) -> None:
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = total - passed

    print("\n" + "=" * 60)
    print("GATEKEEPER SUMMARY")
    print("=" * 60)
    print(f"  Total  : {total}")
    print(f"  Passed : {passed}")
    print(f"  Failed : {failed}")

    if results:
        faith_scores = [r["faithfulness"] for r in results if "faithfulness" in r]
        if faith_scores:
            avg = sum(faith_scores) / len(faith_scores)
            print(f"  Avg Faithfulness : {avg:.3f}")

    print("=" * 60)
    if all_passed:
        print("RESULT: PASSED — pipeline meets quality threshold.")
    else:
        print("RESULT: FAILED — pipeline does not meet quality threshold.")
        print("        Fix the issues above before merging.")
    print("=" * 60)


def main() -> None:
    args = parse_args()

    dataset = load_golden_dataset(args.dataset)
    print(f"[INFO] Loaded {len(dataset)} golden dataset entries.")

    pipe = Pipeline()
    print(f"[INFO] Model: {pipe.cfg.generation.ollama_model} | PDF: {args.pdf}")

    chunks = pipe.ingest(args.pdf)
    print(f"[INFO] Chunks indexed: {len(chunks)}")

    evaluator = RAGASEvaluator(pipe.cfg.generation)

    all_passed, results = run_evaluation(pipe, evaluator, dataset, args.threshold)

    print_summary(results, all_passed)

    # Save results to file for CI artifact upload
    output_path = Path("eval_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[INFO] Results saved to {output_path}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
