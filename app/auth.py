"""
Simple JSON-backed auth for NeuralDoc.
Stores users in users.json with hashed passwords.
"""
import hashlib
import json
from pathlib import Path

from filelock import FileLock

_USERS_FILE = Path("users.json")
_LOCK = FileLock(str(_USERS_FILE) + ".lock")


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _load_users() -> dict:
    if not _USERS_FILE.exists():
        return {}
    try:
        return json.loads(_USERS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_users(users: dict) -> None:
    _USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


def signup(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password are required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    with _LOCK:
        users = _load_users()
        if username in users:
            return False, "Username already taken."
        users[username] = {"password_hash": _hash(password)}
        _save_users(users)
    return True, "Account created! You can now sign in."


def login(username: str, password: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password are required."
    users = _load_users()
    user = users.get(username)
    if not user or user["password_hash"] != _hash(password):
        return False, "Invalid username or password."
    return True, username
