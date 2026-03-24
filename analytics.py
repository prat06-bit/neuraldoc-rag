"""Query analytics tracker — saves to analytics.json."""
import json
from datetime import datetime
from pathlib import Path

ANALYTICS_FILE = Path("analytics.json")


def _load() -> dict:
    if not ANALYTICS_FILE.exists():
        return {"queries": [], "total": 0, "refused": 0, "total_latency_ms": 0}
    try:
        return json.loads(ANALYTICS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"queries": [], "total": 0, "refused": 0, "total_latency_ms": 0}


def _save(data: dict) -> None:
    ANALYTICS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def record_query(query: str, latency_ms: float, refused: bool, model: str = "llama3.1:8b") -> None:
    data = _load()
    data["queries"].append({
        "query": query[:120],
        "latency_ms": round(latency_ms, 1),
        "refused": refused,
        "model": model,
        "timestamp": datetime.now().isoformat(),
    })
    data["total"] += 1
    if refused:
        data["refused"] += 1
    data["total_latency_ms"] = data.get("total_latency_ms", 0) + latency_ms
    # Keep only last 200 queries to limit file size
    data["queries"] = data["queries"][-200:]
    _save(data)


def get_stats() -> dict:
    data = _load()
    total = data.get("total", 0)
    refused = data.get("refused", 0)
    total_lat = data.get("total_latency_ms", 0)
    answered = total - refused
    return {
        "total_queries":    total,
        "answered":         answered,
        "refused":          refused,
        "refusal_rate":     round((refused / total * 100) if total > 0 else 0, 1),
        "avg_latency_ms":   round((total_lat / total) if total > 0 else 0, 0),
        "recent":           list(reversed(data.get("queries", [])))[:5],
    }


def reset_analytics() -> None:
    _save({"queries": [], "total": 0, "refused": 0, "total_latency_ms": 0})
