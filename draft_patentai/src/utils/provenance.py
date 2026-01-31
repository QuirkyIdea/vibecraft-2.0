from __future__ import annotations

from typing import Dict, List, Tuple


def build_provenance_index(
    pages: List[dict],
    blocks: List[dict],
) -> Tuple[List[dict], Dict[str, dict]]:
    """
    Build a provenance index keyed by deterministic IDs.
    The source text is derived from the extracted block text without rewriting.
    """
    provenance_index: Dict[str, dict] = {}

    blocks_by_page: Dict[int, List[dict]] = {}
    for block in blocks:
        blocks_by_page.setdefault(block["page_number"], []).append(block)

    for page in pages:
        page_number = page["page_number"]
        page_blocks = blocks_by_page.get(page_number, [])

        offset = 0
        for block in page_blocks:
            text = block.get("text", "")
            start_offset = offset
            end_offset = start_offset + len(text)
            prov_id = f"p{page_number}s{start_offset}e{end_offset}"

            block["provenance_id"] = prov_id
            provenance_index[prov_id] = {
                "page_number": page_number,
                "start_offset": start_offset,
                "end_offset": end_offset,
                "source_text": text,
            }

            # Add a single newline separator between blocks to keep offsets stable.
            offset = end_offset + 1

    return blocks, provenance_index

