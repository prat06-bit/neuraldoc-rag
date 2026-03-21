from rag.config import load_config
from rag.ingestion.pdf_parser import ParserFactory
from rag.ingestion.chunker import Chunker
from rag.retrieval.vector_store import VectorStore
from rag.retrieval.hybrid_retriever import HybridRetriever
from rag.generation.graph import RAGGraph


def main():
    cfg = load_config()
    print(f"Provider: {cfg.generation.provider} | Model: {cfg.generation.ollama_model}")

    chunks = Chunker(cfg.chunking).chunk(
        ParserFactory.create(cfg.ingestion.parser_strategy, cfg.ingestion).parse("sample.pdf")
    )
    print(f"Chunks: {len(chunks)}")

    store = VectorStore(cfg.retrieval)
    store.add_chunks(chunks)

    retriever = HybridRetriever(store, cfg.retrieval)
    retriever.build_bm25(chunks)

    query = "What was the progression free survival result for combination therapy?"
    result = RAGGraph(cfg.generation, retriever).run(query)

    print("\n=== ANSWER ===")
    print(result["response"])
    print("\n=== REFERENCES ===")
    for r in result["references"]:
        print(" -", r)


if __name__ == "__main__":
    main()