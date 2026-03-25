from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

@dataclass
class EvaluationResult:
    faithfulness: float = 0.0
    context_precision: float = 0.0
    answer_relevancy: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)

    def passed(self, threshold: float = 0.85) -> bool:
        return self.faithfulness >= threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "faithfulness": round(self.faithfulness, 4),
            "context_precision": round(self.context_precision, 4),
            "answer_relevancy": round(self.answer_relevancy, 4),
            "passed": self.passed(),
            "details": self.details,
        }

class RAGASEvaluator:
    def __init__(self, config: Any) -> None:
        self.config = config
        self._llm = None

    def evaluate(
        self,
        query: str,
        answer: str,
        contexts: list[str],
        ground_truth: str = "",
    ) -> EvaluationResult:
        faithfulness = self._score_faithfulness(answer, contexts)
        context_precision = self._score_context_precision(query, contexts)
        answer_relevancy = self._score_answer_relevancy(query, answer)

        details: dict[str, Any] = {
            "query": query,
            "answer_preview": answer[:200],
            "num_contexts": len(contexts),
            "ground_truth": ground_truth,
        }

        if ground_truth:
            details["citations_present"] = self._check_citations(
                answer, ground_truth
            )
        return EvaluationResult(
            faithfulness=faithfulness,
            context_precision=context_precision,
            answer_relevancy=answer_relevancy,
            details=details,
        )
 
    def _score_faithfulness(self, answer: str, contexts: list[str]) -> float:
        if not answer or not contexts:
            return 0.0

        combined_context = "\n\n".join(contexts)

        prompt = f"""You are a strict fact-checker.

CONTEXT:
{combined_context}

ANSWER:
{answer}

Task: List each factual claim in the ANSWER. For each claim, check if it is DIRECTLY stated or clearly implied by the CONTEXT.

Respond with ONLY valid JSON, no other text:
{{"claims": [{{"claim": "...", "supported": true}}, {{"claim": "...", "supported": false}}]}}"""""

        try:
            response = self._ask_llm(prompt)
            data = self._parse_json(response)
            claims: list[dict[str, Any]] = data.get("claims", [])
            if not claims:
                return 1.0
            supported = sum(1 for c in claims if c.get("supported", False))
            return supported / len(claims)
        except Exception:
            return self._heuristic_faithfulness(answer, combined_context)

    # Metric 2: Context Precision

    def _score_context_precision(self, query: str, contexts: list[str]) -> float:
        if not contexts:
            return 0.0

        relevant = 0
        for ctx in contexts:
            prompt = f"""Is the following PASSAGE relevant to answering the QUESTION?
Answer with ONLY "yes" or "no".

QUESTION: {query}

PASSAGE: {ctx[:500]}

Answer:"""
            try:
                response = self._ask_llm(prompt).strip().lower()
                if response.startswith("yes"):
                    relevant += 1
            except Exception:
                # Heuristic fallback
                query_words = set(query.lower().split())
                ctx_words = set(ctx.lower().split())
                if len(query_words & ctx_words) >= 2:
                    relevant += 1

        return relevant / len(contexts)

    # Metric 3: Answer Relevancy
    
    def _score_answer_relevancy(self, query: str, answer: str) -> float:
        """
        Ask LLM to score how well the answer addresses the question (0.0-1.0).
        """
        if not answer:
            return 0.0

        prompt = f"""Rate how well the ANSWER addresses the QUESTION on a scale of 0.0 to 1.0.
1.0 = completely and directly answers the question.
0.5 = partially answers the question.
0.0 = does not answer the question at all.

QUESTION: {query}

ANSWER: {answer[:600]}

Respond with ONLY a decimal number between 0.0 and 1.0 (e.g. 0.85). No other text."""

        try:
            response = self._ask_llm(prompt).strip()
            score = float(re.search(r"[01]?\.\d+|[01]", response).group())  # type: ignore[union-attr]
            return max(0.0, min(1.0, score))
        except Exception:
            # Heuristic: if answer is non-empty and not a refusal
            refusal = "does not contain sufficient evidence"
            return 0.1 if refusal in answer.lower() else 0.7

    # ------------------------------------------------------------------
    # LLM helper
    # ------------------------------------------------------------------

    def _ask_llm(self, prompt: str) -> str:
        """Send a prompt to Ollama and return the response text."""
        if self._llm is None:
            try:
                from langchain_ollama import ChatOllama  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ImportError(
                    "langchain-ollama required. Install: uv add langchain-ollama"
                ) from exc
            self._llm = ChatOllama(
                model=self.config.ollama_model,
                base_url=self.config.ollama_base_url,
                temperature=0.0,
            )

        from langchain_core.messages import HumanMessage  # type: ignore[import-untyped]
        response = self._llm.invoke([HumanMessage(content=prompt)])
        return str(response.content)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        """Extract and parse first JSON object from text."""
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in response.")
        return json.loads(match.group())

    @staticmethod
    def _heuristic_faithfulness(answer: str, context: str) -> float:
        """Simple word-overlap fallback when LLM call fails."""
        sentences = [s.strip() for s in re.split(r"[.!?]", answer) if len(s.strip()) > 20]
        if not sentences:
            return 1.0
        supported = sum(
            1 for s in sentences
            if any(word in context.lower() for word in s.lower().split() if len(word) > 5)
        )
        return supported / len(sentences)

    @staticmethod
    def _check_citations(answer: str, ground_truth: str) -> bool:
        numbers = re.findall(r"\d+\.?\d*", ground_truth)
        return all(num in answer for num in numbers[:3])
