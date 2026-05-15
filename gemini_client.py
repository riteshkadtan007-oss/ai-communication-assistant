"""
Gemini API client.

Uses raw REST (no google-generativeai SDK) so this stays lightweight
and will play nice with Buildozer for Android later.

Public API:
    client = GeminiClient(api_key="AIza...", model="gemini-2.0-flash")
    client.is_configured()           # bool
    client.transform(text, tone, lang=None)   # str, raises GeminiError
    client.ping()                    # bool — quick key health check

Errors are exposed as GeminiError with a user-friendly message — show
e.args[0] / str(e) directly in the UI.
"""
from __future__ import annotations

import time
import requests

from prompts import build_prompt


API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
# `gemini-flash-lite-latest` is the free-tier-friendly alias. The non-lite
# `gemini-flash-latest` requires billing on most accounts now. Lite quality
# is still very good for short text rewriting tasks.
# To use a heavier model (paid tier): gemini-flash-latest, gemini-2.5-flash, etc.
# Run `python list_models.py YOUR_KEY` to see what's available on your key.
DEFAULT_MODEL = "gemini-flash-lite-latest"
REQUEST_TIMEOUT_S = 25
MAX_INPUT_CHARS = 8000   # hard cap on user input length


class GeminiError(Exception):
    """Surfaced to the UI as-is. Message should be user-readable."""


class GeminiClient:
    def __init__(self, api_key: str = "", model: str = DEFAULT_MODEL):
        self.api_key = (api_key or "").strip()
        self.model = model or DEFAULT_MODEL

    # ---- public API ----

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def transform(self, text: str, tone: str, lang: str | None = None) -> str:
        """Run a transformation. Returns the result, or raises GeminiError."""
        if not self.is_configured():
            raise GeminiError(
                "No API key set. Open Settings (⚙) and paste your free Gemini API key."
            )

        text = (text or "").strip()
        if not text:
            raise GeminiError("Please enter some text first.")
        if len(text) > MAX_INPUT_CHARS:
            raise GeminiError(
                f"Text is too long ({len(text)} chars). Max is {MAX_INPUT_CHARS}."
            )

        prompt = build_prompt(tone, text, lang)
        return self._call_with_retry(prompt)

    def ping(self) -> bool:
        """Quick health check — returns True if the key + model work."""
        try:
            self._call_once("Reply with exactly the word: ok")
            return True
        except Exception:
            return False

    # ---- internals ----

    def _call_with_retry(self, prompt: str, max_attempts: int = 3) -> str:
        """Retry only on transient network errors. Never retry on auth/quota."""
        last_net_err: Exception | None = None
        for attempt in range(max_attempts):
            try:
                return self._call_once(prompt)
            except GeminiError:
                # User-facing errors (bad key, quota, blocked content) — don't retry.
                raise
            except (requests.Timeout, requests.ConnectionError) as e:
                last_net_err = e
                if attempt < max_attempts - 1:
                    time.sleep(1.5 * (attempt + 1))  # 1.5s, then 3s
        raise GeminiError(
            f"Network error: couldn't reach Gemini. Check your internet and try again."
        )

    def _call_once(self, prompt: str) -> str:
        url = f"{API_BASE}/{self.model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            },
        }
        headers = {"Content-Type": "application/json"}

        resp = requests.post(
            url,
            params={"key": self.api_key},
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT_S,
        )

        if resp.status_code == 200:
            return self._parse_response(resp.json())

        # Error path — try to extract a clean message
        try:
            err_msg = resp.json().get("error", {}).get("message", "")
        except Exception:
            err_msg = ""
        err_msg = err_msg or resp.text[:200]

        status = resp.status_code
        if status == 400 and ("API key" in err_msg or "API_KEY" in err_msg):
            raise GeminiError("Invalid API key. Re-check it in Settings.")
        if status == 400 and "model" in err_msg.lower():
            raise GeminiError(
                f"Model '{self.model}' not available with this key. "
                "Try 'gemini-2.0-flash' or 'gemini-1.5-flash-latest'."
            )
        if status == 401 or status == 403:
            raise GeminiError(
                "API key was rejected. Make sure it's a Gemini key from aistudio.google.com."
            )
        if status == 429:
            # 429 can mean true rate limit OR "model not on your free tier"
            # OR "billing not enabled". Include the raw message so we can tell.
            raise GeminiError(
                f"Quota/rate error (429) from Gemini for model '{self.model}'. "
                f"Raw message: {err_msg}. "
                f"Fix: try model 'gemini-1.5-flash-latest' (universal free tier), "
                f"or wait 60s if this is a true rate limit."
            )
        if 500 <= status < 600:
            raise GeminiError("Gemini is having issues right now. Try again in a moment.")

        raise GeminiError(f"API error ({status}): {err_msg}")

    @staticmethod
    def _parse_response(data: dict) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            # Most commonly: prompt blocked by safety filter
            feedback = data.get("promptFeedback", {})
            reason = feedback.get("blockReason", "unknown")
            raise GeminiError(
                f"Response was blocked by Gemini's safety filter ({reason}). "
                "Try rewording your input."
            )

        # Sometimes the response itself gets blocked even with a candidate
        first = candidates[0]
        finish_reason = first.get("finishReason", "")
        parts = first.get("content", {}).get("parts", [])
        if not parts:
            if finish_reason == "SAFETY":
                raise GeminiError(
                    "Gemini blocked the output for safety. Try different wording."
                )
            raise GeminiError("Empty response from Gemini. Try again.")

        text = parts[0].get("text", "").strip()
        if not text:
            raise GeminiError("Gemini returned an empty result. Try again.")
        return text
