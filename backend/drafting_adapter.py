from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class DraftSection:
    heading: str
    content: str


@dataclass(frozen=True)
class DraftingResult:
    output: str
    sections: List[DraftSection]


class DraftingAdapterError(RuntimeError):
    pass


@contextmanager
def _working_directory(path: str):
    previous = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(previous)


class DraftPatenAIFacade:
    """
    Thin adapter around draft_patentai services.
    Keeps draft_patentai logic intact and exposes a minimal interface.
    """

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = project_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "draft_patentai")
        )
        if not os.path.isdir(self.project_root):
            raise DraftingAdapterError("draft_patentai directory not found.")
        if self.project_root not in sys.path:
            sys.path.insert(0, self.project_root)

    def generate(self, *, text: str, document_id: str, mode: str) -> DraftingResult:
        if mode not in {"patent", "research"}:
            raise DraftingAdapterError("Unsupported drafting mode.")
        if not text.strip():
            raise DraftingAdapterError("Drafting input text is empty.")

        try:
            from src.services.drafting import generate_draft
            from src.services.extraction import extract_from_text
            from src.services.postprocess import postprocess_section
            from src.services.structuring import extract_primitives
            from src.utils.text import normalize_newlines
        except Exception as exc:
            raise DraftingAdapterError("Unable to import draft_patentai services.") from exc

        try:
            with _working_directory(self.project_root):
                normalized = normalize_newlines(text)
                extraction = extract_from_text(document_id, normalized)
                primitives = extract_primitives(extraction, domain=mode)
                draft_sections = generate_draft(primitives, mode=mode)
                final_text = postprocess_section(draft_sections, document_id, section=mode)
        except Exception as exc:
            raise DraftingAdapterError("Draft generation failed.") from exc

        return DraftingResult(output=final_text, sections=_split_sections(final_text))


def _split_sections(text: str) -> List[DraftSection]:
    sections: List[DraftSection] = []
    current_heading: Optional[str] = None
    buffer: List[str] = []

    def flush():
        if current_heading:
            content = "\n".join(buffer).strip()
            sections.append(DraftSection(heading=current_heading, content=content))

    for line in text.splitlines():
        stripped = line.strip()
        is_heading = (
            stripped
            and stripped == stripped.upper()
            and len(stripped) <= 120
            and all(char.isalpha() or char.isspace() for char in stripped.replace("&", "").replace("-", ""))
        )
        if is_heading:
            flush()
            current_heading = stripped
            buffer = []
            continue
        buffer.append(line)

    flush()
    return sections
