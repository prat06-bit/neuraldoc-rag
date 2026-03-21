from __future__ import annotations
import os
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field
from rag.exceptions import ConfigurationError

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

class IngestionConfig(BaseModel):
    parser_strategy: str = "pdfplumber"
    header_font_size_threshold: float = 13.0
    header_margin_fraction: float = 0.08
    footer_margin_fraction: float = 0.92

class ChunkingConfig(BaseModel):
    min_tokens: int = 500
    max_tokens: int = 800
    tiktoken_encoding: str = "cl100k_base"

class RetrievalConfig(BaseModel):
    embedding_model: str = "all-MiniLM-L6-v2"
    alpha: float = Field(default=0.5, ge=0.0, le=1.0)
    rrf_k: int = 60
    k_initial: int = 20
    k_final: int = 5
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    similarity_threshold: float = 0.35

class GenerationConfig(BaseModel):
    provider: str = "ollama"
    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://localhost:11434"
    openai_model: str = "gpt-4o"
    temperature: float = 0.0
    max_tokens: int = 2048

class EvaluationConfig(BaseModel):
    faithfulness_threshold: float = 0.85
    judge_model: str = "llama3.1:8b"

class RAGConfig(BaseModel):
    domain: str = "medical_research"
    ingestion: IngestionConfig = Field(default_factory=IngestionConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)

def load_config(config_path=None):
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    if not path.exists():
        return RAGConfig()
    with open(path, "r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh) or {}
    return RAGConfig(**raw)