from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypedDict

from rag.config import GenerationConfig
from rag.exceptions import InsufficientEvidenceError
from rag.generation.prompts import REFUSAL_MESSAGE, SYSTEM_PROMPT, build_user_prompt
from rag.retrieval.hybrid_retriever import HybridRetriever
from rag.retrieval.vector_store import ScoredChunk

# Graph state schema

class RAGState(TypedDict):
    query: str
    retrieved: list[ScoredChunk]
    context_passages: list[dict[str, str]]
    response: str
    refused: bool
    references: list[str]

# RAG Graph

class RAGGraph:
    def __init__(
        self,
        config: GenerationConfig,
        retriever: HybridRetriever,
    ) -> None:
        self.config = config
        self.retriever = retriever
        self._graph = self._build_graph()

    # Public API

    def run(self, query: str) -> dict[str, Any]:      
       initial_state: RAGState = {
            "query": query,
            "retrieved": [],
            "context_passages": [],
            "response": "",
            "refused": False,
            "references": [],
        }
        final_state = self._graph.invoke(initial_state)
        return {
            "response": final_state["response"],
            "references": final_state["references"],
            "refused": final_state["refused"],
            "retrieved": final_state["retrieved"],
        }

    # Graph construction

    def _build_graph(self):  # type: ignore[return]
        try:
            from langgraph.graph import END, StateGraph  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "LangGraph is required. Install with: uv add langgraph"
            ) from exc

        graph = StateGraph(RAGState)
        graph.add_node("retrieve", self._node_retrieve)
        graph.add_node("generate", self._node_generate)
        graph.add_node("refuse", self._node_refuse)
        graph.set_entry_point("retrieve")
        graph.add_conditional_edges(
            "retrieve",
            self._route_after_retrieve,
            {"generate": "generate", "refuse": "refuse"},
        )
        graph.add_edge("generate", END)
        graph.add_edge("refuse", END)
        return graph.compile()

    # Nodes

    def _node_retrieve(self, state: RAGState) -> RAGState:
        try:
            results = self.retriever.retrieve(state["query"])
            state["retrieved"] = results
            state["context_passages"] = self._to_context_passages(results)
            state["refused"] = False
        except InsufficientEvidenceError:
            state["retrieved"] = []
            state["context_passages"] = []
            state["refused"] = True
        return state

    def _node_generate(self, state: RAGState) -> RAGState:
        llm = self._get_llm()
        user_prompt = build_user_prompt(state["query"], state["context_passages"])

        try:
            from langchain_core.messages import HumanMessage, SystemMessage  # type: ignore[import-untyped]
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
            response = llm.invoke(messages)
            answer: str = response.content
        except Exception as exc:
            answer = f"Generation failed: {exc}"

        state["response"] = answer
        state["references"] = self._extract_references(state["context_passages"])
        return state

    def _node_refuse(self, state: RAGState) -> RAGState:
        """Return the hard refusal message."""
        state["response"] = REFUSAL_MESSAGE
        state["refused"] = True
        state["references"] = []
        return state

    # Routing

    @staticmethod
    def _route_after_retrieve(state: RAGState) -> str:
        return "refuse" if state["refused"] else "generate"

    # LLM factory — selects Ollama or OpenAI based on config.provider

    def _get_llm(self):  # type: ignore[return]
        provider = self.config.provider.lower()

        if provider == "ollama":
            return self._get_ollama_llm()
        elif provider == "openai":
            return self._get_openai_llm()
        else:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                "Set config.generation.provider to 'ollama' or 'openai'."
            )

    def _get_ollama_llm(self):  # type: ignore[return]
        try:
            from langchain_ollama import ChatOllama  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "langchain-ollama is required. Install with: uv add langchain-ollama"
            ) from exc

        return ChatOllama(
            model=self.config.ollama_model,
            base_url=self.config.ollama_base_url,
            temperature=self.config.temperature,
            num_predict=self.config.max_tokens,
        )

    def _get_openai_llm(self):  # type: ignore[return]
        try:
            from langchain_openai import ChatOpenAI  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "langchain-openai is required. Install with: uv add langchain-openai"
            ) from exc

        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable is not set."
            )
        return ChatOpenAI(
            model=self.config.openai_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=api_key,
        )

    # Helpers

    @staticmethod
    def _to_context_passages(results: list[ScoredChunk]) -> list[dict[str, str]]:
        passages: list[dict[str, str]] = []
        for sc in results:
            source = Path(sc.chunk.metadata.source).stem
            breadcrumb = " > ".join(sc.chunk.metadata.breadcrumb_path)
            passages.append({
                "text": sc.chunk.text,
                "source": source,
                "page": str(sc.chunk.metadata.page),
                "breadcrumb": breadcrumb,
            })
        return passages

    @staticmethod
    def _extract_references(passages: list[dict[str, str]]) -> list[str]:
        seen: set[str] = set()
        refs: list[str] = []
        for p in passages:
            ref = f"{p.get('source', 'Unknown')}, p. {p.get('page', '?')}"
            if ref not in seen:
                seen.add(ref)
                refs.append(ref)
        return refs
