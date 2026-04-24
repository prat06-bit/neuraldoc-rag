from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    source: str
    page: int
    breadcrumb_path: list[str] = []
    char_start: int | None = None
    char_end: int | None = None
    extra: dict[str, Any] = {}


class DocumentChunk(BaseModel):
    chunk_id: str
    text: str
    token_count: int
    metadata: ChunkMetadata


class ParsedPage(BaseModel):
    page_number: int
    text: str
    tables: list[str] = []
    is_multi_column: bool = False
    raw_blocks: list[dict[str, Any]] = []


class ParsedDocument(BaseModel):
    source: str
    total_pages: int
    pages: list[ParsedPage]
    parse_strategy: str