import json
from datetime import datetime
from pathlib import Path

# pip install filelock
from filelock import FileLock

ANALYTICS_DIR = Path("analytics_data")


def _get_file(username: str) -> Path:
    ANALYTICS_DIR.mkdir(exist_ok=True)
    return ANALYTICS_DIR / f"{username}.json"


def _get_lock(username: str) -> FileLock:
    ANALYTICS_DIR.mkdir(exist_ok=True)
    return FileLock(str(_get_file(username)) + ".lock")


def _load(username: str) -> dict:
    f = _get_file(username)
    if not f.exists():
        return {"queries": [], "total": 0, "refused": 0, "total_latency_ms": 0}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {"queries": [], "total": 0, "refused": 0, "total_latency_ms": 0}


def _save(data: dict, username: str) -> None:
    _get_file(username).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def record_query(query: str, latency_ms: float, refused: bool, model: str = "llama3.1:8b", username: str = "default") -> None:
    with _get_lock(username):
        data = _load(username)
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
        _save(data, username)


def get_stats(username: str = "default") -> dict:
    data = _load(username)
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


def reset_analytics(username: str = "default") -> None:
    with _get_lock(username):
        _save({"queries": [], "total": 0, "refused": 0, "total_latency_ms": 0}, username)
