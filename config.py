"""
Persist user settings (API key, model choice) to disk.

Storage location depends on platform:
- Android: app's private writable dir (App.user_data_dir),
  resolves to /data/user/0/<package>/files/
- Mac / Linux / Windows desktop running the Kivy app:
  ~/Library/Application Support/aikeyboard/ (or platform equivalent)
- CLI tools (test_gemini.py) and any time no Kivy app is running:
  ~/.ai_keyboard/  (a simple stable path in the user's home folder)
"""
import json
from pathlib import Path

# Single source of truth — defined in gemini_client.py, imported here so
# changing the default in one place actually changes it everywhere.
from gemini_client import DEFAULT_MODEL


def _get_config_dir() -> Path:
    """
    Return a writable directory for our config file.

    When the Kivy app is running, use App.user_data_dir — this is the
    correct, platform-specific writable location (especially critical on
    Android, where Path.home() points to a place the app can't write).

    When no app is running (e.g., running test_gemini.py from a terminal),
    fall back to ~/.ai_keyboard/ for backwards compatibility.
    """
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app is not None and app.user_data_dir:
            return Path(app.user_data_dir)
    except Exception:
        pass
    return Path.home() / ".ai_keyboard"


def _config_file() -> Path:
    return _get_config_dir() / "config.json"


def _ensure_dir() -> None:
    _get_config_dir().mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    cfg = _config_file()
    if not cfg.exists():
        return {}
    try:
        with open(cfg, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Corrupt or unreadable — treat as empty rather than crash.
        return {}


def save_config(data: dict) -> None:
    _ensure_dir()
    with open(_config_file(), "w", encoding="utf-8") as f:
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
