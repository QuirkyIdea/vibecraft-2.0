from __future__ import annotations

import re
from typing import Iterable, List


_PARA_SPLIT_RE = re.compile(r"\n\s*\n", re.MULTILINE)


def normalize_newlines(text: str) -> str:
    """Normalize line endings without rewriting content."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def split_paragraphs(text: str) -> List[str]:
    """
    Split on blank lines only. This avoids summarizing or rewriting content.
    """
    if not text:
        return []
    normalized = normalize_newlines(text)
    parts = [p for p in _PARA_SPLIT_RE.split(normalized) if p.strip()]
    return parts


def safe_truncate(text: str, limit: int) -> str:
    """
    Deterministic truncation for logging/metadata only.
    """
    if len(text) <= limit:
        return text
    return text[:limit]


def iter_nonempty_lines(text: str) -> Iterable[str]:
    for line in normalize_newlines(text).split("\n"):
        if line.strip():
            yield line

