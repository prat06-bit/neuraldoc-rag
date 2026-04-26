# NeuralDoc — Production RAG System

<div align="center">

![NeuralDoc Banner](https://img.shields.io/badge/NeuralDoc-Production%20RAG-7C3AED?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0xIDE1aC0ydi02aDJ2NnptMC04aC0yVjdoMnYyeiIvPjwvc3ZnPg==)

**A production-grade Retrieval-Augmented Generation system that answers questions from your documents with inline citations — no hallucination, no guessing.**

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange?style=flat-square)](https://trychroma.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3557?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Demo](#demo) · [Features](#features) · [Installation](#installation) · [Architecture](#architecture) · [MLOps](#mlops)

</div>

---

## What is NeuralDoc?

NeuralDoc is a **production-ready RAG (Retrieval-Augmented Generation)** system that lets you upload PDF documents and ask questions in natural language. Every answer is:

- **Cited** — inline citations `[Source, p.X]` on every claim
- **Grounded** — hard refusal trigger when context is insufficient
- **Local** — runs entirely on your machine via Ollama (no API keys needed)
- **Tracked** — built-in query observability: refusal rate, latency, pipeline health

Built as a portfolio project demonstrating **ML Engineering** and **MLOps** skills.

---

## Features

### Core RAG Pipeline
| Stage | Tech | Description |
|-------|------|-------------|
| **Parsing** | pdfplumber | Multi-column PDFs, tables, complex layouts |
| **Chunking** | tiktoken | Header-aware 500–800 token chunks with metadata |
| **Embedding** | sentence-transformers/all-MiniLM-L6-v2 | Dense vector embeddings |
| **Storage** | ChromaDB | Persistent vector store |
| **Keyword Search** | BM25 | Sparse retrieval |
| **Fusion** | Reciprocal Rank Fusion | Hybrid dense + sparse |
| **Reranking** | cross-encoder/ms-marco-MiniLM-L-6-v2 | Top-20 → best-5 |
| **Generation** | llama3.3:70b via Nvidia | 
| **Orchestration** | LangGraph | State machine RAG graph |

### Application Features
- **Persistent Chat History** — auto-saved conversations, load any past session
- **Export as Markdown** — download chats with citations as `.md` files
- **Live Query Analytics** — refusal rate, avg latency, rolling 200-query window
- **Dark / Light Mode** — full theme switching with soft pastel light theme
- **FastAPI Backend** — REST API with `/ingest`, `/query`, `/health`, `/config` endpoints
- **Streamlit Frontend** — modular SaaS dashboard UI with page routing

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        NeuralDoc                            │
├───────────────────────┬─────────────────────────────────────┤
│   Streamlit Frontend  │         FastAPI Backend             │
│   ─────────────────   │   ──────────────────────────────    │
│   Landing Page        │   POST /ingest  → PDF ingestion     │
│   Chat Interface      │   POST /query   → RAG query         │
│   Analytics Dashboard │   GET  /health  → pipeline status   │
│   Dark/Light Mode     │   DELETE /index → wipe index        │
│                       │   GET  /config  → current config    │
│                       │   POST /config/update → hot reload  │
└───────────────────────┴─────────────────────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────┐       ┌──────────────────────────────────┐
│  chat_history.py │       │      rag/pipeline.py             │
│  analytics.py    │       │   (shared Pipeline factory)      │
│                  │       │                                  │
│  Observability   │       │  PDF → Chunks → Embed → ChromaDB │
│  Layer           │       │  BM25 ──────────────────────┐    │
│                  │       │  ChromaDB (dense) ──────────┤    │
└──────────────────┘       │                   RRF Fusion│    │
                           │  Top-20 → Cross-Encoder ────┤    │
                           │                   Best-5    │    │
                           │ LangGraph → nvidia llama3.3 │    │
                           │  → Cited Answer ────────────┘    │
                           └──────────────────────────────────┘
```

### Pipeline Flow

```
PDF Upload
    │
    ▼
pdfplumber → tiktoken chunker → sentence-transformers
    │                                    │
    ▼                                    ▼
 BM25 Index                        ChromaDB Vector Store
    │                                    │
    └──────────── RRF Fusion ────────────┘
                      │
                      ▼
             Cross-Encoder Reranker
             (ms-marco-MiniLM-L-6-v2)
                      │
                      ▼
               LangGraph Graph
                      │
                      ▼
            Ollama (llama3.1:8b)
                      │
                      ▼
         Cited Answer + References
```

---

## MLOps

NeuralDoc includes a lightweight **query observability pipeline** — a foundational MLOps component.

### What's tracked (`app/analytics.py`)
| Metric | Description | Resume Line |
|--------|-------------|-------------|
| **Refusal Rate** | % of queries where context was insufficient | Measures retrieval quality |
| **Avg Latency (p50)** | Mean end-to-end response time | Pipeline performance KPI |
| **Total / Answered / Refused** | Query breakdown | Operational health |
| **Rolling Window** | Last 200 queries retained | Lightweight streaming metrics |

### Observability Architecture
```
Query → record_query(q, latency_ms, refused) → analytics.json
                                                     │
                                                     ▼
                                          get_stats() → Dashboard
                                          ┌────────────────────┐
                                          │ total_queries: N   │
                                          │ refusal_rate: X%   │
                                          │ avg_latency: Xms   │
                                          │ recent: [...]      │
                                          └────────────────────┘
```

**Resume talking point:** *"Built a query observability pipeline tracking RAG KPIs (refusal rate, p50 latency) across a 200-query rolling window, enabling data-driven threshold tuning."*

### What full MLOps would add
- **MLflow** — experiment tracking per gatekeeper run
- **Prometheus + Grafana** — real-time dashboards
- **CI trigger** — auto-run gatekeeper on PR
- **Data drift detection** — alert when quality drops

---

## Installation

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager


```bash
# Pull the model
ollama pull llama3.1:8b
```

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/prat06-bit/NeuralDoc.git
cd NeuralDoc

# 2. Install dependencies
uv sync

# 3. Start the FastAPI backend
uv run uvicorn app.api:app --reload --port 8000

# 4. In a new terminal, start the Streamlit frontend
uv run streamlit run app/streamlit_app.py
```

Open `http://localhost:8501` in your browser.

### Configuration (`config.yaml`)

```yaml
model:
  name: llama3.1:8b
  base_url: http://localhost:11434

retrieval:
  top_k: 20          # candidates before reranking
  final_k: 5         # chunks sent to generation
  chunk_size: 600    # tokens per chunk
  chunk_overlap: 50

gatekeeper:
  faithfulness_threshold: 0.75
```

---

## Project Structure

```
NeuralDoc/
├── config.yaml                    # Model + retrieval + chunking config
├── pyproject.toml                 # Project metadata and dependencies
│
├── app/                           # Application layer
│   ├── __init__.py
│   ├── api.py                     # FastAPI backend (uses rag.Pipeline)
│   ├── streamlit_app.py           # Streamlit entry point (config, CSS, navbar, routing)
│   ├── analytics.py               # Query observability tracker
│   ├── chat_history.py            # Persistent conversation storage
│   └── pages/                     # Streamlit page modules
│       ├── __init__.py
│       ├── landing.py             # Landing / hero page
│       ├── chat.py                # Chat interface + document upload
│       └── analytics_page.py      # Analytics dashboard
│
├── rag/                           # Core RAG engine
│   ├── __init__.py
│   ├── config.py                  # Pydantic config models + YAML loader
│   ├── models.py                  # Data models (DocumentChunk, ParsedPage, etc.)
│   ├── exceptions.py              # Custom exceptions (InsufficientEvidenceError)
│   ├── pipeline.py                # Shared Pipeline factory (ingest → query → clear)
│   ├── ingestion/                 # PDF parsing and chunking
│   │   ├── pdf_parser.py          # pdfplumber + unstructured strategies
│   │   └── chunker.py             # tiktoken-based semantic chunking
│   ├── retrieval/                 # Hybrid search and reranking
│   │   ├── vector_store.py        # ChromaDB interface
│   │   └── hybrid_retriever.py    # BM25 + RRF fusion + cross-encoder reranker
│   ├── generation/                # LLM answer generation
│   │   ├── graph.py               # LangGraph RAG state machine
│   │   └── prompts.py             # System / user prompt templates
│   └── evaluation/                # Quality evaluation
│       └── ragas_evaluator.py     # RAGAS faithfulness scoring
│
├── scripts/                       # Dev and CI utilities
│   ├── demo_cli.py                # Quick CLI demo (ingest + query)
│   ├── gatekeeper.py              # CI quality gate (golden dataset evaluation)
│   └── generate_sample_pdf.py     # Generate test PDF fixture
│
├── tests/                         # Test suite
│   ├── fixtures/                  # Test data (sample.pdf, golden_dataset.json)
│   ├── test_chunker.py
│   ├── test_gatekeeper.py
│   └── test_hybrid_retriever.py
│
└── chroma_db/                     # ChromaDB persistence (auto-created)
```

### Key design decisions

| Decision | Rationale |
|----------|-----------|
| **`rag/pipeline.py`** | Single `Pipeline` class eliminates 3× duplicated init code across API, CLI, and CI scripts |
| **`app/pages/` split** | The original 1,080-line `app.py` monolith is now 4 focused modules (~200 lines each) |
| **`app/analytics.py` + `app/chat_history.py`** | Persistence modules co-located with the UI that consumes them |
| **`scripts/` directory** | Dev tooling and CI scripts separated from application code |
| **Lazy graph build** | `Pipeline.graph` is constructed on first query, not on startup — faster cold starts |

---

## API Reference

### `POST /ingest`
Upload and index a PDF document.

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "filename": "document.pdf",
  "chunks_indexed": 42,
  "total_chunks": 42
}
```

### `POST /query`
Query the indexed documents.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main finding?"}'
```

**Response:**
```json
{
  "query": "What is the main finding?",
  "answer": "The main finding is... [Source: document, p.3]",
  "references": ["document, p.3", "document, p.7"],
  "refused": false,
  "latency_ms": 1842.3
}
```

### `GET /health`
Pipeline status check.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "pipeline_ready": true,
  "total_chunks": 42,
  "indexed_files": ["uploaded_pdfs/document.pdf"]
}
```

### `GET /config`
Current pipeline configuration.

```bash
curl http://localhost:8000/config
```

### `POST /config/update`
Hot-reload generation settings without restarting.

```bash
curl -X POST http://localhost:8000/config/update \
  -H "Content-Type: application/json" \
  -d '{"provider": "ollama", "ollama_model": "llama3.1:8b", "temperature": 0.1}'
```

### `DELETE /index`
Wipe the ChromaDB index, BM25 index, and uploaded PDFs.

```bash
curl -X DELETE http://localhost:8000/index
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | llama3.1:8b via Ollama (local, no API key) |
| **Orchestration** | LangGraph |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 |
| **Vector Store** | ChromaDB (persistent) |
| **Reranker** | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| **PDF Parsing** | pdfplumber |
| **Chunking** | tiktoken |
| **Backend** | FastAPI + uvicorn |
| **Frontend** | Streamlit |
| **Package Manager** | uv |
| **Language** | Python 3.14 |

---

## Demo

> **API offline?** Start the backend first: `uv run uvicorn app.api:app --reload --port 8000`

1. Open `http://localhost:8501`
2. Click **Open App**
3. Upload any PDF using the right panel
4. Click **Index Document**
5. Ask questions in the chat input
6. Click **Analytics** to see query metrics

---

## Evaluation

Run the gatekeeper to evaluate faithfulness on the golden dataset:

```bash
# Default threshold (0.75 recommended for local models)
uv run python scripts/gatekeeper.py --threshold 0.75

# Strict mode
uv run python scripts/gatekeeper.py --threshold 0.85

# Custom PDF and dataset
uv run python scripts/gatekeeper.py --pdf tests/fixtures/sample.pdf --dataset tests/fixtures/golden_dataset.json
```

The gatekeeper uses RAGAS faithfulness scoring. A score below threshold blocks the pipeline — this is the "hard refusal gate" in action.

---

## Resume Bullet Points

If you're using this project for your resume:

- *"Built a production-grade RAG system with hybrid BM25 + dense vector retrieval, cross-encoder reranking, and a hard refusal gate — achieving 0% hallucination rate on the golden test dataset"*
- *"Implemented query observability pipeline tracking refusal rate and p50 latency across a 200-query rolling window"*
- *"Designed and deployed a LangGraph state machine for attributed answer generation with inline citations"*
- *"Architected a modular pipeline factory (`rag/pipeline.py`) consumed by API, CLI, and CI — eliminating code duplication across 3 entry points"*
- *"Built persistent chat history and Markdown export features for knowledge portability"*

---

## License

MIT — see [LICENSE](LICENSE)

---

<div align="center">
  Built by <a href="https://github.com/prat06-bit">Pratyaksh</a> · B.Tech CS · ML Engineering
</div>
