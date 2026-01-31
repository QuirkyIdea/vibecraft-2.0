from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class PdfPageInfo:
    page_number: int
    width: float
    height: float
    rotation: int | None


def _classify_block(text: str, font_size: float | None, page_height: float, max_font: float) -> str:
    stripped = text.strip()
    if not stripped:
        return "paragraph"
    lower = stripped.lower()
    if lower.startswith("figure") or lower.startswith("fig.") or lower.startswith("table"):
        return "caption"
    if stripped.startswith(("-", "•", "*")) or stripped[:2].isdigit():
        return "list"
    if font_size and max_font > 0:
        if font_size >= max_font * 0.9 and page_height > 0.0:
            return "title"
        if font_size >= max_font * 0.7:
            return "heading"
    if stripped.isupper() and len(stripped) <= 80:
        return "heading"
    return "paragraph"


def _extract_with_pdfminer(pdf_path: str) -> Tuple[List[PdfPageInfo], List[dict]]:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTChar, LTTextContainer

    pages: List[PdfPageInfo] = []
    blocks: List[dict] = []

    for page_number, layout in enumerate(extract_pages(pdf_path), start=1):
        width = float(getattr(layout, "width", 0.0))
        height = float(getattr(layout, "height", 0.0))
        rotation = int(getattr(layout, "rotation", 0) or 0)
        pages.append(PdfPageInfo(page_number, width, height, rotation))

        text_containers: List[LTTextContainer] = [
            element for element in layout if isinstance(element, LTTextContainer)
        ]

        font_sizes: List[float] = []
        for container in text_containers:
            for char in container:
                if isinstance(char, LTChar):
                    font_sizes.append(float(char.size))
        max_font = max(font_sizes) if font_sizes else 0.0

        for container in text_containers:
            text = container.get_text()
            if not text.strip():
                continue
            char_sizes: List[float] = [
                float(char.size) for char in container if isinstance(char, LTChar)
            ]
            block_font = median(char_sizes) if char_sizes else None
            block_type = _classify_block(text, block_font, height, max_font)
            x0, y0, x1, y1 = container.bbox
            blocks.append(
                {
                    "block_id": f"b{len(blocks) + 1}",
                    "page_number": page_number,
                    "block_type": block_type,
                    "text": text,
                    "bbox": [float(x0), float(y0), float(x1), float(y1)],
                }
            )

    return pages, blocks


def _extract_with_pypdf(pdf_path: str) -> Tuple[List[PdfPageInfo], List[dict]]:
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    pages: List[PdfPageInfo] = []
    blocks: List[dict] = []
    block_id = 1

    for idx, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        rotation = int(page.get("/Rotate", 0) or 0)
        pages.append(PdfPageInfo(idx, width, height, rotation))

        text = page.extract_text() or ""
        if text.strip():
            blocks.append(
                {
                    "block_id": f"b{block_id}",
                    "page_number": idx,
                    "block_type": "paragraph",
                    "text": text,
                    "bbox": [0.0, 0.0, width, height],
                }
            )
            block_id += 1

    return pages, blocks


def extract_pdf(pdf_path: str) -> Tuple[List[dict], List[dict]]:
    """
    Deterministic PDF extraction using pdfminer.six with pypdf fallback.
    Returns:
      - pages: list of page metadata dicts
      - blocks: list of text blocks with bbox
    """
    try:
        pages, blocks = _extract_with_pdfminer(pdf_path)
    except Exception:
        pages, blocks = _extract_with_pypdf(pdf_path)

    page_dicts = [
        {
            "page_number": p.page_number,
            "width": p.width,
            "height": p.height,
            "rotation": p.rotation,
        }
        for p in pages
    ]
    return page_dicts, blocks

