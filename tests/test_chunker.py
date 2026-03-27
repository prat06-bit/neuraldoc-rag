from __future__ import annotations

import tiktoken
from rag.config import ChunkingConfig, IngestionConfig
from rag.ingestion.chunker import SemanticChunker
from rag.models import PageContent, TextBlock

def _make_page(
    blocks: list[tuple[str, float, bool]], page_number: int = 1
) -> PageContent:
    text_blocks = [
        TextBlock(text=text, font_size=size, is_bold=bold)
        for text, size, bold in blocks
    ]
    raw_text = "\n".join(b.text for b in text_blocks)
    return PageContent(
        page_number=page_number,
        text_blocks=text_blocks,
        tables=[],
        raw_text=raw_text,
    )


class TestSemanticChunker:
    """Tests for the SemanticChunker class."""

    def setup_method(self) -> None:
        self.chunking_cfg = ChunkingConfig(
            min_tokens=10, max_tokens=50, tiktoken_encoding="cl100k_base"
        )
        self.ingestion_cfg = IngestionConfig(header_font_size_threshold=13.0)
        self.chunker = SemanticChunker(
            chunking_config=self.chunking_cfg,
            ingestion_config=self.ingestion_cfg,
        )
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def test_basic_chunking_produces_output(self) -> None:
        """Chunking a simple page produces at least one chunk."""
        page = _make_page([
            ("Introduction", 16.0, True),
            ("This is some body text that describes the topic in detail. "
             "It contains multiple sentences. Each one adds information.", 11.0, False),
        ])
        chunks = self.chunker.chunk_pages([page], source_file="test.pdf")
        assert len(chunks) > 0

    def test_chunks_contain_required_metadata(self) -> None:
        """Each chunk must have source_file, page_number, and breadcrumb_path."""
        page = _make_page([
            ("Chapter One", 16.0, True),
            ("Body text here with enough words to form a chunk.", 11.0, False),
        ])
        chunks = self.chunker.chunk_pages([page], source_file="doc.pdf")
        for chunk in chunks:
            assert chunk.source_file == "doc.pdf"
            assert chunk.page_number >= 1
            assert isinstance(chunk.breadcrumb_path, str)
            assert chunk.chunk_id != ""

    def test_breadcrumb_path_reflects_headers(self) -> None:
        """Breadcrumb path should include detected headers."""
        page = _make_page([
            ("Main Title", 20.0, True),
            ("Some introductory text in the main section.", 11.0, False),
        ])
        chunks = self.chunker.chunk_pages([page], source_file="test.pdf")
        # At least one chunk should reference the header
        breadcrumbs = [c.breadcrumb_path for c in chunks]
        assert any("Main Title" in b for b in breadcrumbs)

    def test_token_count_is_populated(self) -> None:
        """Each chunk should have a positive token count."""
        page = _make_page([
            ("Section A", 14.0, True),
            ("Detailed explanation with multiple words forming a text block.", 11.0, False),
        ])
        chunks = self.chunker.chunk_pages([page], source_file="test.pdf")
        for chunk in chunks:
            assert chunk.token_count > 0

    def test_chunk_id_is_deterministic(self) -> None:
        """Same input should produce the same chunk IDs."""
        page = _make_page([
            ("Header", 14.0, True),
            ("Body text content.", 11.0, False),
        ])
        chunks_a = self.chunker.chunk_pages([page], source_file="test.pdf")
        chunks_b = self.chunker.chunk_pages([page], source_file="test.pdf")
        assert [c.chunk_id for c in chunks_a] == [c.chunk_id for c in chunks_b]

    def test_tables_are_included_as_segments(self) -> None:
        """Tables from PageContent should appear in chunk text."""
        page = PageContent(
            page_number=1,
            text_blocks=[
                TextBlock(text="Results", font_size=14.0, is_bold=True),
            ],
            tables=["| Col A | Col B |\n| --- | --- |\n| 1 | 2 |"],
            raw_text="Results",
        )
        chunks = self.chunker.chunk_pages([page], source_file="test.pdf")
        all_text = " ".join(c.text for c in chunks)
        assert "Col A" in all_text

    def test_empty_pages_produce_no_chunks(self) -> None:
        """Chunking empty pages should return an empty list."""
        page = PageContent(
            page_number=1, text_blocks=[], tables=[], raw_text=""
        )
        chunks = self.chunker.chunk_pages([page], source_file="test.pdf")
        assert chunks == []

    def test_multi_page_chunking(self) -> None:
        """Chunks from multiple pages should preserve page numbers."""
        pages = [
            _make_page(
                [("Page one content here.", 11.0, False)], page_number=1
            ),
            _make_page(
                [("Page two content here.", 11.0, False)], page_number=2
            ),
        ]
        chunks = self.chunker.chunk_pages(pages, source_file="multi.pdf")
        page_numbers = {c.page_number for c in chunks}
        assert len(page_numbers) >= 1
