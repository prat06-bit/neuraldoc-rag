from __future__ import annotations

REFUSAL_MESSAGE = (
    "The provided documentation does not contain sufficient evidence "
    "to answer this query."
)

SYSTEM_PROMPT = """You are a precise, domain-specific question-answering assistant.
You answer questions exclusively from the provided context passages."""

def build_user_prompt(query: str, context_passages: list[dict[str, str]]) -> str:
    if not context_passages:
        return (
            f"Question: {query}\n\n"
            "Context: [No context provided]\n\n"
            "Answer:"
        )

    context_block = _format_context(context_passages)

    return (
        f"Question: {query}\n\n"
        f"Context Passages:\n{context_block}\n\n"
        "Instructions:\n"
        "- Answer the question using only the context above.\n"
        "- Cite every fact inline as [Source Name, p. X].\n"
        "- End with a References section.\n\n"
        "Answer:"
    )


def _format_context(passages: list[dict[str, str]]) -> str:
    lines: list[str] = []
    for i, p in enumerate(passages, start=1):
        source = p.get("source", "Unknown")
        page = p.get("page", "?")
        breadcrumb = p.get("breadcrumb", "")
        text = p.get("text", "").strip()

        header = f"[{i}] Source: {source} | Page: {page}"
        if breadcrumb:
            header += f" | Section: {breadcrumb}"
        lines.append(header)
        lines.append(text)
        lines.append("")

    return "\n".join(lines)
