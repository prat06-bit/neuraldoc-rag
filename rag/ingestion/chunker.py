
import hashlib
import re
from typing import Iterator

import tiktoken

from rag.config import ChunkingConfig
from rag.models import ChunkMetadata, DocumentChunk, ParsedDocument, ParsedPage


# ---------------------------------------------------------------------------
# Heading detection
# ---------------------------------------------------------------------------

# Matches lines that look like headings:
#   - Markdown: ## Title
#   - Numbered: 1. Title / 1.1 Title
#   - ALL CAPS line (≤ 80 chars)
_HEADING_RE = re.compile(
    r"^(?:"
    r"#{1,6}\s+.+"           # Markdown headings
    r"|(?:\d+\.)+\d*\s+\S.+" # Numbered headings  e.g. 1.2 Introduction
    r"|\d+\.\s+[A-Z].+"      # 1. Title
    r"|[A-Z][A-Z\s]{3,79}$"  # ALL CAPS headings
    r")$"
)


def _is_heading(line: str, font_sizes: list[float], threshold: float) -> bool:
    """Return True if *line* looks like a section heading."""
    line = line.strip()
    if not line:
        return False
    if _HEADING_RE.match(line):
        return True
    # Font-size heuristic: if the line's average font size exceeds threshold
    if font_sizes and sum(font_sizes) / len(font_sizes) >= threshold:
        return True
    return False


# ---------------------------------------------------------------------------
# Sentence splitter (lightweight, no NLTK dependency)
# ---------------------------------------------------------------------------

_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_END_RE.split(text) if s.strip()]


# ---------------------------------------------------------------------------
# Core chunker
# ---------------------------------------------------------------------------

class Chunker:
    """Converts a ParsedDocument into token-bounded DocumentChunks."""

    def __init__(self, config: ChunkingConfig) -> None:
        self.config = config
        self._enc = tiktoken.get_encoding(config.tiktoken_encoding)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chunk(self, doc: ParsedDocument) -> list[DocumentChunk]:
        """Process all pages and return the complete chunk list."""
        chunks: list[DocumentChunk] = []
        for page in doc.pages:
            chunks.extend(self._chunk_page(page, doc.source))
        return chunks

    # ------------------------------------------------------------------
    # Per-page processing
    # ------------------------------------------------------------------

    def _chunk_page(
        self, page: ParsedPage, source: str
    ) -> list[DocumentChunk]:
        """Split one page into chunks respecting heading boundaries."""
        lines = page.text.splitlines()

        # Build a flat list of (line_text, is_heading, font_sizes) tuples.
        # Font size data comes from raw_blocks if available.
        font_size_map = self._build_font_size_map(page)

        sections: list[tuple[list[str], str]] = []  # (lines, heading_label)
        current_heading = ""
        current_lines: list[str] = []

        for line in lines:
            fs = font_size_map.get(line.strip(), [])
            if _is_heading(line, fs, self.config.min_tokens):
                # Flush current section
                if current_lines:
                    sections.append((current_lines, current_heading))
                current_heading = line.strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_lines, current_heading))

        # Also append any extracted tables as standalone chunks
        table_sections: list[tuple[list[str], str]] = [
            ([tbl], f"{current_heading} [TABLE]") for tbl in page.tables
        ]
        sections.extend(table_sections)

        # Build breadcrumb stack (simple single-level for now)
        chunks: list[DocumentChunk] = []
        for section_lines, heading in sections:
            text = "\n".join(section_lines).strip()
            if not text:
                continue
            breadcrumb = [heading] if heading else []
            for chunk in self._split_to_chunks(text, source, page.page_number, breadcrumb):
                chunks.append(chunk)

        return chunks

    # ------------------------------------------------------------------
    # Token-aware splitting
    # ------------------------------------------------------------------

    def _split_to_chunks(
        self,
        text: str,
        source: str,
        page: int,
        breadcrumb: list[str],
    ) -> Iterator[DocumentChunk]:
        """Yield chunks within [min_tokens, max_tokens] from *text*."""
        tokens = self._count_tokens(text)

        if tokens <= self.config.max_tokens:
            # Entire section fits in one chunk
            if tokens >= self.config.min_tokens or text.strip():
                yield self._make_chunk(text, source, page, breadcrumb)
            return

        # Section too large — split by sentence and re-accumulate
        sentences = _split_sentences(text)
        buffer: list[str] = []
        buffer_tokens = 0

        for sentence in sentences:
            s_tokens = self._count_tokens(sentence)
            if buffer_tokens + s_tokens > self.config.max_tokens and buffer:
                yield self._make_chunk(" ".join(buffer), source, page, breadcrumb)
                buffer = []
                buffer_tokens = 0
            buffer.append(sentence)
            buffer_tokens += s_tokens

        if buffer:
            yield self._make_chunk(" ".join(buffer), source, page, breadcrumb)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_chunk(
        self,
        text: str,
        source: str,
        page: int,
        breadcrumb: list[str],
    ) -> DocumentChunk:
        token_count = self._count_tokens(text)
        chunk_id = hashlib.sha256(
            f"{source}:{page}:{text[:64]}".encode()
        ).hexdigest()[:16]

        return DocumentChunk(
            chunk_id=chunk_id,
            text=text,
            token_count=max(token_count, 1),
            metadata=ChunkMetadata(
                source=source,
                page=page,
                breadcrumb_path=breadcrumb,
            ),
        )

    def _count_tokens(self, text: str) -> int:
        return len(self._enc.encode(text))

    @staticmethod
    def _build_font_size_map(page: ParsedPage) -> dict[str, list[float]]:
        """Map stripped line text → list of font sizes from raw_blocks."""
        mapping: dict[str, list[float]] = {}
        for block in page.raw_blocks:
            sizes: list[float] = block.get("font_sizes", [])
            if sizes:
                # Use bbox as a proxy key — not perfect but avoids full span walk
                mapping[str(block.get("bbox", ""))] = sizes
        return mapping
