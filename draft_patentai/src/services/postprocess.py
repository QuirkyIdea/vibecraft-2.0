from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional


_PARA_SPLIT_RE = re.compile(r"\n\s*\n", re.MULTILINE)
_LIST_RE = re.compile(r"^\s*([\-*•]|\d+[.)])\s+")
_URL_RE = re.compile(r"https?://|doi:\s*\S+", re.IGNORECASE)


@dataclass(frozen=True)
class StyleProfile:
    line_width: int
    paragraph_break: str
    bullet: str


def _style_from_seed(seed_key: str) -> StyleProfile:
    digest = hashlib.sha256(seed_key.encode("utf-8")).hexdigest()
    seed = int(digest[:8], 16)

    widths = [72, 78, 80, 88]
    breaks = ["\n\n", "\n\n\n"]
    bullets = ["-", "*"]

    return StyleProfile(
        line_width=widths[seed % len(widths)],
        paragraph_break=breaks[(seed // 3) % len(breaks)],
        bullet=bullets[(seed // 7) % len(bullets)],
    )


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _split_paragraphs(text: str) -> List[str]:
    if not text.strip():
        return []
    return [p for p in _PARA_SPLIT_RE.split(text) if p.strip()]


def _is_list_paragraph(lines: Iterable[str]) -> bool:
    for line in lines:
        if line.strip() and _LIST_RE.match(line):
            return True
    return False


def _reflow_words(text: str, width: int) -> str:
    words = text.split()
    if not words:
        return ""
    lines = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= width:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return "\n".join(lines)


def _format_list(lines: List[str], bullet: str) -> str:
    formatted: List[str] = []
    for line in lines:
        if not line.strip():
            continue
        match = _LIST_RE.match(line)
        if not match:
            formatted.append(line.rstrip())
            continue
        marker = match.group(1)
        content = line[match.end() :].strip()
        if marker.isdigit() or marker.endswith((")", ".")):
            formatted.append(f"{marker} {content}")
        else:
            formatted.append(f"{bullet} {content}")
    return "\n".join(formatted)


def _should_reflow(paragraph: str) -> bool:
    if _URL_RE.search(paragraph):
        return False
    if "\\\\" in paragraph:
        return False
    return True


def postprocess_section(
    text: str,
    document_id: str,
    section: str,
    style_override: Optional[StyleProfile] = None,
) -> str:
    """
    Deterministic post-processing that introduces human-like formatting
    variability without paraphrasing or altering word order.
    """
    style = style_override or _style_from_seed(f"{document_id}:{section}")
    normalized = _normalize_newlines(text)
    paragraphs = _split_paragraphs(normalized)

    formatted_paragraphs: List[str] = []
    for paragraph in paragraphs:
        lines = [line.rstrip() for line in paragraph.split("\n") if line.strip()]
        if not lines:
            continue
        if _is_list_paragraph(lines):
            formatted_paragraphs.append(_format_list(lines, style.bullet))
            continue
        flat = " ".join(lines)
        if _should_reflow(flat):
            formatted_paragraphs.append(_reflow_words(flat, style.line_width))
        else:
            formatted_paragraphs.append("\n".join(lines))

    return style.paragraph_break.join(formatted_paragraphs).strip()

