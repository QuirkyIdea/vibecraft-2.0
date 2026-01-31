from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Tuple


_SECTION_RULES = {
    "problem_statement": [
        "problem",
        "background",
        "limitation",
        "motivation",
        "need",
        "challenge",
    ],
    "technical_solution": [
        "solution",
        "summary",
        "invention",
        "approach",
        "method",
        "proposed",
    ],
    "system_components": [
        "system",
        "architecture",
        "component",
        "device",
        "apparatus",
        "module",
        "subsystem",
    ],
    "process_steps": [
        "process",
        "steps",
        "procedure",
        "workflow",
        "algorithm",
        "method",
    ],
    "advantages": [
        "advantage",
        "benefit",
        "improve",
        "improvement",
        "efficient",
        "robust",
    ],
    "results": [
        "result",
        "evaluation",
        "experiment",
        "performance",
        "analysis",
        "finding",
    ],
}

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _split_sentences(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]


def _match_section(text: str) -> Optional[str]:
    normalized = _normalize(text)
    for section, keywords in _SECTION_RULES.items():
        for kw in keywords:
            if kw in normalized:
                return section
    return None


def _collect_evidence(
    section: str,
    blocks: Iterable[dict],
    evidence: Dict[str, List[dict]],
    include_sentence_split: bool = False,
) -> None:
    for block in blocks:
        block_text = block.get("text", "").strip()
        if not block_text:
            continue
        if include_sentence_split:
            for sentence in _split_sentences(block_text):
                evidence[section].append(
                    {
                        "text": sentence,
                        "provenance_id": block.get("provenance_id"),
                        "block_id": block.get("block_id"),
                    }
                )
        else:
            evidence[section].append(
                {
                    "text": block_text,
                    "provenance_id": block.get("provenance_id"),
                    "block_id": block.get("block_id"),
                }
            )


def _is_heading(block: dict) -> bool:
    return block.get("block_type") in {"heading", "title"}


def _ordered_blocks(extraction_result: dict) -> List[dict]:
    blocks = extraction_result.get("blocks", [])
    return list(blocks)


def extract_primitives(extraction_result: dict, domain: str) -> Dict[str, object]:
    """
    Rule-based conversion of extracted text into invention/research primitives.
    This is deterministic and does not add or rewrite any content.
    """
    blocks = _ordered_blocks(extraction_result)

    evidence: Dict[str, List[dict]] = {
        "problem_statement": [],
        "technical_solution": [],
        "system_components": [],
        "process_steps": [],
        "advantages": [],
        "results": [],
    }

    active_section: Optional[str] = None
    buffer: List[dict] = []

    def flush_buffer() -> None:
        nonlocal buffer, active_section
        if active_section and buffer:
            _collect_evidence(active_section, buffer, evidence)
        buffer = []

    for block in blocks:
        text = block.get("text", "").strip()
        if not text:
            continue

        if _is_heading(block):
            flush_buffer()
            active_section = _match_section(text)
            continue

        if active_section:
            buffer.append(block)
            continue

        # No active section: classify by cues at the sentence level.
        section = _match_section(text)
        if section:
            _collect_evidence(section, [block], evidence, include_sentence_split=True)

    flush_buffer()

    return {
        "domain": domain,
        "primitives": evidence,
    }

