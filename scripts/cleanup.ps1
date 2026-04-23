# NeuralDoc — Post-Refactor Cleanup Script
# Run this from the project root to complete Phases 1 & 2 (delete + move old files)
# Review before running!

# ── Phase 1: Delete dead / duplicate code ──────────────────────────────────
$toDelete = @(
    "config.py",                    # stale duplicate of rag/config.py
    "rag\vector_store.py",          # stale duplicate of rag/retrieval/vector_store.py
    "rag\retrieval\reranker.py",    # broken duplicate (imports non-existent model)
    "upload_section_snippet.py",    # orphan code fragment
    "RAG_Chat.py",                  # superseded by app/streamlit_app.py
    "app.py",                       # superseded by app/streamlit_app.py
    "main.py",                      # superseded by scripts/demo_cli.py
    "gatekeeper.py",                # superseded by scripts/gatekeeper.py
    "generate_sample_pdf.py",       # superseded by scripts/generate_sample_pdf.py
    "analytics.py",                 # superseded by app/analytics.py
    "chat_history.py",              # superseded by app/chat_history.py
    "tempCodeRunnerFile.python",    # IDE artifact
    "my_pyright_out.txt",           # IDE artifact
    "pyright.json",                 # IDE artifact
    "pyright2.json",                # IDE artifact
    "pyright_utf8.json"             # IDE artifact
)

foreach ($f in $toDelete) {
    if (Test-Path $f) {
        Remove-Item $f -Force
        Write-Host "  Deleted: $f" -ForegroundColor Red
    } else {
        Write-Host "  Skipped (not found): $f" -ForegroundColor DarkGray
    }
}

# ── Phase 2: Move test fixtures ────────────────────────────────────────────
$fixturesDir = "tests\fixtures"
if (-not (Test-Path $fixturesDir)) { New-Item -ItemType Directory -Path $fixturesDir -Force | Out-Null }

$toMove = @(
    @{ From = "sample.pdf";          To = "tests\fixtures\sample.pdf" },
    @{ From = "golden_dataset.json"; To = "tests\fixtures\golden_dataset.json" },
    @{ From = "eval_results.json";   To = "tests\fixtures\eval_results.json" }
)

foreach ($m in $toMove) {
    if (Test-Path $m.From) {
        Move-Item $m.From $m.To -Force
        Write-Host "  Moved: $($m.From) -> $($m.To)" -ForegroundColor Green
    }
}

# ── Phase 2: Rename pyrightconfig ────────────────────────────────────────────
$weirdName = "Pyrightconfig · JSON"
if (Test-Path $weirdName) {
    Rename-Item $weirdName "pyrightconfig.json" -Force
    Write-Host "  Renamed: '$weirdName' -> pyrightconfig.json" -ForegroundColor Green
}

Write-Host "`nCleanup complete!" -ForegroundColor Cyan
Write-Host "New entry points:" -ForegroundColor Cyan
Write-Host "  Streamlit:  streamlit run app/streamlit_app.py" -ForegroundColor White
Write-Host "  FastAPI:    uvicorn app.api:app --reload --port 8000" -ForegroundColor White
Write-Host "  CLI demo:   python scripts/demo_cli.py" -ForegroundColor White
Write-Host "  CI gate:    python scripts/gatekeeper.py" -ForegroundColor White
