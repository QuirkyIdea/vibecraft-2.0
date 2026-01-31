from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

from src.services.llm_client import generate_text, is_llm_configured


_SYSTEM_PREPROMPT = (
    "You are a drafting assistant. Use only the provided primitives. "
    "Do not invent facts, steps, results, or claims. "
    "Maintain formal, professional tone and follow section-specific instructions."
)


def _collect_text(evidence: List[dict]) -> List[str]:
    lines = [item.get("text", "").strip() for item in evidence if item.get("text")]
    return [line for line in lines if line]


def _has_any(*items: List[str]) -> bool:
    return any(item for item in items)


def _load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _prompt_path(mode: str, section: str) -> str:
    return os.path.join("src", "prompts", mode, f"{section}.txt")


def _section_input_for_patent(primitives: Dict[str, List[dict]], section: str) -> Dict[str, object]:
    problem = _collect_text(primitives.get("problem_statement", []))
    solution = _collect_text(primitives.get("technical_solution", []))
    components = _collect_text(primitives.get("system_components", []))
    steps = _collect_text(primitives.get("process_steps", []))
    advantages = _collect_text(primitives.get("advantages", []))
    results = _collect_text(primitives.get("results", []))

    if section == "title":
        return {"problem_statement": problem, "technical_solution": solution}
    if section == "abstract":
        return {
            "problem_statement": problem,
            "technical_solution": solution,
            "system_components": components,
            "advantages": advantages or results,
        }
    if section == "background":
        return {"problem_statement": problem}
    if section == "summary":
        return {
            "technical_solution": solution,
            "system_components": components,
            "process_steps": steps,
        }
    if section == "brief_description_of_drawings":
        return {}
    if section == "detailed_description":
        return {
            "system_components": components,
            "process_steps": steps,
            "advantages": advantages,
            "results": results,
        }
    if section == "claims":
        return {
            "technical_solution": solution,
            "system_components": components,
            "process_steps": steps,
        }
    return {}


def _section_input_for_research(primitives: Dict[str, List[dict]], section: str) -> Dict[str, object]:
    problem = _collect_text(primitives.get("problem_statement", []))
    solution = _collect_text(primitives.get("technical_solution", []))
    components = _collect_text(primitives.get("system_components", []))
    steps = _collect_text(primitives.get("process_steps", []))
    results = _collect_text(primitives.get("results", []))
    advantages = _collect_text(primitives.get("advantages", []))

    if section == "title":
        return {"problem_statement": problem, "technical_solution": solution}
    if section == "abstract":
        return {
            "problem_statement": problem,
            "technical_solution": solution,
            "results": results,
            "advantages": advantages,
        }
    if section == "introduction":
        return {"problem_statement": problem, "technical_solution": solution}
    if section == "related_work":
        return {"problem_statement": problem}
    if section == "methods":
        return {
            "technical_solution": solution,
            "system_components": components,
            "process_steps": steps,
        }
    if section == "results":
        return {"results": results}
    if section == "discussion":
        return {"results": results, "advantages": advantages}
    if section == "conclusion":
        return {"advantages": advantages, "results": results}
    if section == "references":
        return {}
    return {}


def _section_has_content(section_input: Dict[str, object]) -> bool:
    for value in section_input.values():
        if isinstance(value, list) and any(value):
            return True
        if isinstance(value, str) and value.strip():
            return True
    return False


def _render_prompt(mode: str, section: str, section_input: Dict[str, object]) -> str:
    prompt = _load_prompt(_prompt_path(mode, section))
    return prompt.replace("{{domain}}", mode).replace(
        "{{section_input_json}}", json.dumps(section_input, ensure_ascii=True)
    )


def _fallback_section(section: str, section_input: Dict[str, object]) -> Optional[str]:
    if not _section_has_content(section_input):
        return None
    parts = []
    for key, value in section_input.items():
        if isinstance(value, list) and value:
            parts.append(" ".join(value))
        elif isinstance(value, str) and value.strip():
            parts.append(value)
    text = " ".join(parts).strip()
    if not text:
        return None
    return text


def _generate_section(mode: str, section: str, section_input: Dict[str, object]) -> Optional[str]:
    if not _section_has_content(section_input):
        return None
    prompt = _render_prompt(mode, section, section_input)
    if is_llm_configured():
        content = generate_text(_SYSTEM_PREPROMPT, prompt)
        if content:
            return content
    return _fallback_section(section, section_input)


def _assemble_sections(sections: List[Tuple[str, str]]) -> str:
    blocks = []
    for heading, content in sections:
        blocks.append(heading.upper())
        blocks.append(content.strip())
    return "\n\n".join(blocks).strip()


def _patent_sections(primitives: Dict[str, List[dict]]) -> List[Tuple[str, str]]:
    ordered = [
        ("title", "TITLE"),
        ("abstract", "ABSTRACT"),
        ("background", "BACKGROUND"),
        ("summary", "SUMMARY"),
        ("brief_description_of_drawings", "BRIEF DESCRIPTION OF DRAWINGS"),
        ("detailed_description", "DETAILED DESCRIPTION"),
        ("claims", "CLAIMS"),
    ]
    sections: List[Tuple[str, str]] = []
    for key, heading in ordered:
        section_input = _section_input_for_patent(primitives, key)
        content = _generate_section("patent", key, section_input)
        if content:
            sections.append((heading, content))
    return sections


def _research_sections(primitives: Dict[str, List[dict]]) -> List[Tuple[str, str]]:
    ordered = [
        ("title", "TITLE"),
        ("abstract", "ABSTRACT"),
        ("introduction", "INTRODUCTION"),
        ("related_work", "RELATED WORK"),
        ("methods", "METHODS"),
        ("results", "RESULTS"),
        ("discussion", "DISCUSSION"),
        ("conclusion", "CONCLUSION"),
        ("references", "REFERENCES"),
    ]
    sections: List[Tuple[str, str]] = []
    for key, heading in ordered:
        section_input = _section_input_for_research(primitives, key)
        content = _generate_section("academic", key, section_input)
        if content:
            sections.append((heading, content))
    return sections


def generate_draft(primitives_result: Dict[str, object], mode: str) -> str:
    primitives = primitives_result.get("primitives", {})
    if mode == "patent":
        return _assemble_sections(_patent_sections(primitives))
    if mode == "research":
        return _assemble_sections(_research_sections(primitives))
    raise ValueError("Unsupported mode")

