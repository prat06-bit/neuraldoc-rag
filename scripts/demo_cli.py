from rag.pipeline import Pipeline


def main():
    pipe = Pipeline()
    print(f"Provider: {pipe.cfg.generation.provider} | Model: {pipe.cfg.generation.ollama_model}")

    chunks = pipe.ingest("sample.pdf")
    print(f"Chunks: {len(chunks)}")

    query = "What was the progression free survival result for combination therapy?"
    result = pipe.query(query)

    print("\n=== ANSWER ===")
    print(result["response"])
    print("\n=== REFERENCES ===")
    for r in result["references"]:
        print(" -", r)


if __name__ == "__main__":
    main()
