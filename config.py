"""
Persist user settings (API key, model choice) to disk.

Stored in ~/.ai_keyboard/config.json so reinstalling the app
doesn't wipe the saved key.
"""
import json
from pathlib import Path

# Single source of truth — defined in gemini_client.py, imported here so
# changing the default in one place actually changes it everywhere.
from gemini_client import DEFAULT_MODEL

CONFIG_DIR = Path.home() / ".ai_keyboard"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Corrupt or unreadable — treat as empty rather than crash.
        return {}


def save_config(data: dict) -> None:
    _ensure_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_api_key() -> str:
    return load_config().get("gemini_api_key", "")


def save_api_key(key: str) -> None:
    data = load_config()
    data["gemini_api_key"] = (key or "").strip()
    save_config(data)


def load_model() -> str:
    return load_config().get("model", DEFAULT_MODEL)


def save_model(model: str) -> None:
    data = load_config()
    data["model"] = model
    save_config(data)
