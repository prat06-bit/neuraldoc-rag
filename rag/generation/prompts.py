from __future__ import annotations

REFUSAL_MESSAGE = (
    "The provided documentation does not contain sufficient evidence "
    "to answer this query."
)

SYSTEM_PROMPT = """You are a precise, domain-specific question-answering assistant.
You answer questions exclusively from the provided context passages.

STRICT RULES:
1. Every factual claim must include an inline citation in the format [Source Name, p. X].
   Example: "The PFS rate was 48.3% [Medical Research Summary Report, p. 1]."
2. You must include a "References" section at the end listing every source cited.
3. If the context does not contain enough information to answer the question,
   respond with exactly: "The provided documentation does not contain sufficient evidence to answer this query."
4. Do not add information from outside the provided context.
5. Do not speculate or infer beyond what the context explicitly states.
6. Use precise, technical language. No emojis. No filler phrases.
"""

# ---------------------------------------------------------------------------
# Context + query prompt builder
# ---------------------------------------------------------------------------

def build_user_prompt(query: str, context_passages: list[dict[str, str]]) -> str:
    """
    Build the user-turn prompt from a query and a list of context passages.

    Parameters
    ----------
    query            : The user's question.
    context_passages : List of dicts with keys:
                         - text       : The chunk text.
                         - source     : File name / document title.
                         - page       : Page number (as string).
                         - breadcrumb : Section path (optional).

    Returns
    -------
    Formatted string ready to send as the user message.
    """
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
