from __future__ import annotations

import json
import os
import urllib.request
from typing import Optional


class LlmClientError(Exception):
    pass


_ENV_LOADED = False


def _load_dotenv() -> None:
    """
    Lightweight .env loader to avoid extra dependencies.
    Only sets variables that are not already defined.
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True

    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dotenv_path = os.path.join(root, ".env")
    if not os.path.exists(dotenv_path):
        return

    try:
        with open(dotenv_path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        return


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    _load_dotenv()
    value = os.getenv(name, default)
    return value if value else default


def is_llm_configured() -> bool:
    return bool(_get_env("DRAFT_LLM_API_KEY"))


def generate_text(system_prompt: str, user_prompt: str) -> Optional[str]:
    """
    Minimal OpenAI-compatible chat completion call using env vars:
      - DRAFT_LLM_API_KEY (required)
      - DRAFT_LLM_API_URL (optional)
      - DRAFT_LLM_MODEL (optional)
    Returns None on any failure so callers can fall back deterministically.
    """
    api_key = _get_env("DRAFT_LLM_API_KEY")
    if not api_key:
        return None

    api_url = _get_env("DRAFT_LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    model = _get_env("DRAFT_LLM_MODEL", "gpt-4o-mini")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
    except Exception:
        return None

    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

