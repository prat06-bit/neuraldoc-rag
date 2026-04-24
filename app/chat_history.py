import json
import uuid
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("chat_history.json")


def _load_raw() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_raw(data: list) -> None:
    HISTORY_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def save_conversation(messages: list, title: str | None = None) -> str:
    if not messages:
        return ""
    all_convs = _load_raw()
    conv_id = str(uuid.uuid4())[:8]
    if title is None:
        first_user = next(
            (m["content"] for m in messages if m["role"] == "user"), "Untitled"
        )
        title = first_user[:48] + ("…" if len(first_user) > 48 else "")
    all_convs.append({
        "id": conv_id,
        "title": title,
        "timestamp": datetime.now().isoformat(),
        "messages": messages,
    })
    _save_raw(all_convs)
    return conv_id


def load_all_conversations() -> list:
    return list(reversed(_load_raw()))


def load_conversation(conv_id: str) -> list:
    for conv in _load_raw():
        if conv["id"] == conv_id:
            return conv["messages"]
    return []


def delete_conversation(conv_id: str) -> None:
    data = [c for c in _load_raw() if c["id"] != conv_id]
    _save_raw(data)


def delete_all_conversations() -> None:
    _save_raw([])


def export_as_markdown(messages: list, title: str = "Chat Export") -> str:
    lines = [f"# {title}", f"_Exported {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"]
    for m in messages:
        role = "**You**" if m["role"] == "user" else "**NeuralDoc**"
        lines.append(f"{role}\n\n{m['content']}\n")
        if m.get("references"):
            lines.append("References: " + ", ".join(m["references"]) + "\n")
        if m.get("refused"):
            lines.append(" Refusal triggered — insufficient evidence_\n")
        lines.append("---\n")
    return "\n".join(lines)