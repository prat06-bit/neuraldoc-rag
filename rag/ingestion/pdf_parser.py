from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Optional, cast

from rag.config import IngestionConfig
from rag.models import ParsedDocument, ParsedPage

# Abstract base

class BasePDFParser(ABC):
    strategy_name: str = "base"

    def __init__(self, config: IngestionConfig) -> None:
        self.config = config

    @abstractmethod
    def parse(self, path: str | Path) -> ParsedDocument:

# pdfplumber strategy 

class PDFPlumberParser(BasePDFParser):
    strategy_name = "pdfplumber"

    def parse(self, path: str | Path) -> ParsedDocument:
        try:
            import pdfplumber  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "pdfplumber is required. Install with: uv add pdfplumber"
            ) from exc

        path = Path(path).resolve()
        pages: list[ParsedPage] = []

        with pdfplumber.open(str(path)) as pdf:
            for i, page in enumerate(pdf.pages):
                # --- Text ---
                raw_text: str = page.extract_text(
                    x_tolerance=3, y_tolerance=3
                ) or ""

                # Strip header/footer margins
                page_height: float = float(page.height)
                header_y = page_height * self.config.header_margin_fraction
                footer_y = page_height * self.config.footer_margin_fraction

                cropped = page.within_bbox(
                    (0, header_y, float(page.width), footer_y),
                    relative=False,
                )
                text: str = cropped.extract_text(
                    x_tolerance=3, y_tolerance=3
                ) or raw_text

                # --- Tables ---
                tables: list[str] = []
                for tbl in page.extract_tables():
                    if tbl:
                        md = self._table_to_markdown(tbl)
                        if md:
                            tables.append(md)

                # --- Multi-column detection (word x-coord clustering) ---
                words = page.extract_words()
                is_multi_column = self._detect_multi_column(words)

                pages.append(
                    ParsedPage(
                        page_number=i + 1,
                        text=text.strip(),
                        tables=tables,
                        is_multi_column=is_multi_column,
                        raw_blocks=[],
                    )
                )

        return ParsedDocument(
            source=str(path),
            total_pages=len(pages),
            pages=pages,
            parse_strategy=self.strategy_name,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _table_to_markdown(table: list[list[str | None]]) -> str:
        """Convert a pdfplumber table (list of rows) to Markdown."""
        rows: list[list[str]] = [
            [str(cell).strip() if cell else "" for cell in row]
            for row in table
            if any(cell for cell in row)
        ]
        if not rows:
            return ""

        col_count = max(len(r) for r in rows)
        padded: list[list[str]] = [
            r + [""] * (col_count - len(r)) for r in rows
        ]

        lines: list[str] = []
        lines.append("| " + " | ".join(padded[0]) + " |")
        lines.append("| " + " | ".join(["---"] * col_count) + " |")
        for i in range(1, len(padded)):
            lines.append("| " + " | ".join(padded[i]) + " |")
        return "\n".join(lines)

    @staticmethod
    def _detect_multi_column(words: list[dict[str, Any]]) -> bool:
        """Return True if x0 coordinates cluster into two groups."""
        if not words:
            return False
        x0s = [float(w.get("x0", 0)) for w in words]
        if not x0s:
            return False
        mid = (max(x0s) + min(x0s)) / 2
        left = [x for x in x0s if x < mid - 30]
        right = [x for x in x0s if x >= mid + 30]
        return bool(left) and bool(right)


# ---------------------------------------------------------------------------
# Unstructured strategy  (optional — heavy, high-accuracy)
# ---------------------------------------------------------------------------

_partition_pdf_fn: Optional[Callable[..., Any]] = None
_UNSTRUCTURED_AVAILABLE = False

try:
    from unstructured.partition.pdf import (  # type: ignore[import-untyped]
        partition_pdf as _imported_partition_pdf,
    )
    _partition_pdf_fn = _imported_partition_pdf
    _UNSTRUCTURED_AVAILABLE = True
except ImportError:
    pass


class UnstructuredParser(BasePDFParser):
    """
    Uses the `unstructured` library for high-fidelity extraction.
    Install: uv add "unstructured[pdf]"
    """

    strategy_name = "unstructured"

    def parse(self, path: str | Path) -> ParsedDocument:
        if not _UNSTRUCTURED_AVAILABLE or _partition_pdf_fn is None:
            raise ImportError(
                "Install with: uv add 'unstructured[pdf]'"
            )

        path = Path(path).resolve()
        elements = _partition_pdf_fn(
            filename=str(path),
            strategy="hi_res",
            infer_table_structure=True,
            include_page_breaks=True,
        )

        page_map: dict[int, dict[str, Any]] = {}
        current_page = 1

        for el in elements:
            page_num: int = current_page
            meta = getattr(el, "metadata", None)
            if meta is not None:
                pn = getattr(meta, "page_number", None)
                if isinstance(pn, int):
                    page_num = pn
                    current_page = pn

            if page_num not in page_map:
                page_map[page_num] = {"text_parts": [], "tables": []}

            category: str = getattr(el, "category", "") or ""
            el_text: str = getattr(el, "text", "") or ""

            if category == "Table":
                html: str = (
                    getattr(getattr(el, "metadata", None), "text_as_html", None)
                    or el_text
                )
                page_map[page_num]["tables"].append(html)
            elif el_text:
                page_map[page_num]["text_parts"].append(el_text)

        pages: list[ParsedPage] = [
            ParsedPage(
                page_number=pnum,
                text="\n".join(entry["text_parts"]),
                tables=entry["tables"],
                is_multi_column=False,
            )
            for pnum, entry in sorted(page_map.items())
        ]

        return ParsedDocument(
            source=str(path),
            total_pages=len(pages),
            pages=pages,
            parse_strategy=self.strategy_name,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, type[BasePDFParser]] = {
    PDFPlumberParser.strategy_name: PDFPlumberParser,
    UnstructuredParser.strategy_name: UnstructuredParser,
}


class ParserFactory:
    @staticmethod
    def create(strategy: str, config: IngestionConfig) -> BasePDFParser:
        cls = _REGISTRY.get(strategy.lower())
        if cls is None:
            available = ", ".join(_REGISTRY.keys())
            raise ValueError(
                f"Unknown parser strategy '{strategy}'. "
                f"Available: {available}"
            )
        return cls(config)

    @staticmethod
    def register(name: str, cls: type[BasePDFParser]) -> None:
        _REGISTRY[name.lower()] = cls
