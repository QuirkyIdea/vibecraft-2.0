from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.utils.pdf import extract_pdf
from src.utils.provenance import build_provenance_index
from src.utils.text import iter_nonempty_lines, normalize_newlines, split_paragraphs


def _sha256_bytes(content: bytes) -> str:
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _base_metadata(
    checksum: str,
    source_filename: Optional[str] = None,
    title_hint: Optional[str] = None,
) -> Dict[str, object]:
    return {
        "title": title_hint or "Untitled",
        "authors": [],
        "created_at": _now_iso(),
        "checksum": checksum,
        "source_filename": source_filename,
    }


def _build_text_blocks(text: str) -> List[dict]:
    blocks: List[dict] = []
    paragraphs = split_paragraphs(text)
    block_id = 1
    for para in paragraphs:
        blocks.append(
            {
                "block_id": f"b{block_id}",
                "page_number": 1,
                "block_type": "paragraph",
                "text": para,
                "bbox": [0.0, 0.0, 0.0, 0.0],
            }
        )
        block_id += 1
    return blocks


def _derive_title_from_text(text: str) -> str:
    for line in iter_nonempty_lines(text):
        return line.strip()
    return "Untitled"


def _extraction_result(
    document_id: str,
    source_type: str,
    language: str,
    metadata: Dict[str, object],
    pages: List[dict],
    blocks: List[dict],
    tables: Optional[List[dict]] = None,
    figures: Optional[List[dict]] = None,
    references: Optional[List[dict]] = None,
    annotations: Optional[Dict[str, list]] = None,
) -> Dict[str, object]:
    tables = tables or []
    figures = figures or []
    references = references or []
    annotations = annotations or {
        "citations": [],
        "equations": [],
        "claims_markers": [],
    }

    blocks, provenance_index = build_provenance_index(pages, blocks)

    return {
        "document_id": document_id,
        "source_type": source_type,
        "language": language,
        "metadata": metadata,
        "pages": pages,
        "blocks": blocks,
        "tables": tables,
        "figures": figures,
        "references": references,
        "annotations": annotations,
        "provenance_index": provenance_index,
    }


def extract_from_text(
    document_id: str,
    text: str,
    language: str = "en",
    metadata_override: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    normalized = normalize_newlines(text)
    checksum = _sha256_bytes(normalized.encode("utf-8"))
    title_hint = _derive_title_from_text(normalized)
    metadata = _base_metadata(checksum=checksum, title_hint=title_hint)

    if metadata_override:
        metadata.update(metadata_override)

    pages = [{"page_number": 1, "width": 0.0, "height": 0.0, "rotation": 0}]
    blocks = _build_text_blocks(normalized)

    return _extraction_result(
        document_id=document_id,
        source_type="text",
        language=language,
        metadata=metadata,
        pages=pages,
        blocks=blocks,
    )


def extract_from_pdf(
    document_id: str,
    pdf_path: str,
    language: str = "en",
    metadata_override: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    with open(pdf_path, "rb") as handle:
        content = handle.read()
    checksum = _sha256_bytes(content)

    pages, blocks = extract_pdf(pdf_path)

    title_hint = None
    if blocks:
        title_hint = blocks[0].get("text", "").strip().split("\n")[0].strip() or None

    metadata = _base_metadata(
        checksum=checksum,
        source_filename=pdf_path.split("\\")[-1].split("/")[-1],
        title_hint=title_hint or "Untitled",
    )
    if metadata_override:
        metadata.update(metadata_override)

    return _extraction_result(
        document_id=document_id,
        source_type="pdf",
        language=language,
        metadata=metadata,
        pages=pages,
        blocks=blocks,
    )

