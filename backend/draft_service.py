"""
Draft Optimization Service for Inventix AI - Phase 6

Generates localized draft improvement suggestions based on:
- Comparative overlap analysis from Phase 5
- Novelty risk context
- Writing quality issues

CRITICAL RULES:
- Do NOT rewrite entire documents
- Do NOT inject new technical claims
- Do NOT claim novelty improvement as fact
- Do NOT overwrite user drafts
- Suggestions must be explainable and rejectable
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from config import get_settings
import ai_service

settings = get_settings()


# ============== Output Schema ==============

class DraftSuggestionOutput(BaseModel):
    """Single suggestion from LLM"""
    original_text_snippet: str
    suggested_revision: str
    reason_for_change: str
    change_type: str  # clarity, specificity, overlap_reduction, structure
    preserves_intent: str  # YES, POSSIBLY, NO


# ============== Prompt Templates ==============

DRAFT_OPTIMIZATION_PROMPT = """You are a writing improvement assistant. Your task is to suggest LOCALIZED improvements to a draft text.

CRITICAL RULES (MANDATORY):
1. Do NOT rewrite the entire document
2. Do NOT add new technical claims or inventions
3. Do NOT claim your suggestions will improve novelty or patentability
4. Do NOT use AI clichés like "leverage", "utilize", "cutting-edge", "revolutionize"
5. Preserve the author's voice and intent
6. Make suggestions sound human-written
7. Each suggestion must be a small, focused change

---

USER'S DRAFT:
{draft_text}

---

OVERLAP CONTEXT (from prior art analysis):
{overlap_context}

---

NOVELTY RISK: {novelty_risk}

---

Based on the draft and overlap context, suggest 3-7 LOCALIZED improvements. Focus on:
1. CLARITY - Making sentences clearer without changing meaning
2. SPECIFICITY - Adding precision where the text is vague
3. OVERLAP_REDUCTION - Rewording to differentiate from existing work (if overlaps exist)
4. STRUCTURE - Improving paragraph flow or organization

For each suggestion:
- Quote the EXACT original text snippet (10-100 characters)
- Provide your suggested revision
- Explain WHY this change helps
- Specify the change type
- Honestly assess if it preserves the author's intent (YES/POSSIBLY/NO)

Respond in JSON format ONLY:
{{
  "suggestions": [
    {{
      "original_text_snippet": "exact quote from draft",
      "suggested_revision": "your improved version",
      "reason_for_change": "explanation of why this helps",
      "change_type": "clarity|specificity|overlap_reduction|structure",
      "preserves_intent": "YES|POSSIBLY|NO"
    }}
  ]
}}"""


NO_OVERLAP_PROMPT = """You are a writing improvement assistant. Your task is to suggest LOCALIZED improvements to a draft text.

CRITICAL RULES (MANDATORY):
1. Do NOT rewrite the entire document
2. Do NOT add new technical claims or inventions
3. Do NOT use AI clichés like "leverage", "utilize", "cutting-edge"
4. Preserve the author's voice and intent
5. Make suggestions sound human-written
6. Each suggestion must be a small, focused change

---

USER'S DRAFT:
{draft_text}

---

No prior art overlap context is available. Focus only on writing quality improvements.

Suggest 3-5 LOCALIZED improvements focusing on:
1. CLARITY - Making sentences clearer
2. SPECIFICITY - Adding precision where vague
3. STRUCTURE - Improving flow

Respond in JSON format ONLY:
{{
  "suggestions": [
    {{
      "original_text_snippet": "exact quote from draft",
      "suggested_revision": "your improved version",
      "reason_for_change": "explanation",
      "change_type": "clarity|specificity|structure",
      "preserves_intent": "YES|POSSIBLY|NO"
    }}
  ]
}}"""


# ============== Service Functions ==============

def generate_draft_suggestions(
    draft_text: str,
    overlap_context: Optional[str] = None,
    novelty_risk: str = "UNKNOWN"
) -> Dict[str, Any]:
    """
    Generate localized draft improvement suggestions.
    
    Returns suggestions that are:
    - Localized (not full rewrites)
    - Explainable (with reasons)
    - Rejectable (user can dismiss)
    """
    # Truncate draft if too long
    draft_text = draft_text[:10000]
    
    # Choose prompt based on whether we have overlap context
    if overlap_context:
        prompt = DRAFT_OPTIMIZATION_PROMPT.format(
            draft_text=draft_text,
            overlap_context=overlap_context[:3000],
            novelty_risk=novelty_risk
        )
    else:
        prompt = NO_OVERLAP_PROMPT.format(draft_text=draft_text)
    
    try:
        response = ai_service.call_llm(prompt, max_tokens=2000)
        
        if not response["success"]:
            return {
                "success": False,
                "suggestions": [],
                "error": response.get("error", "LLM call failed")
            }
        
        # Parse JSON response
        ai_output = response["output"]
        
        try:
            # Handle potential markdown code blocks
            if "```json" in ai_output:
                json_str = ai_output.split("```json")[1].split("```")[0]
            elif "```" in ai_output:
                json_str = ai_output.split("```")[1].split("```")[0]
            else:
                json_str = ai_output
            
            parsed = json.loads(json_str.strip())
            suggestions = parsed.get("suggestions", [])
            
            # Validate and clean suggestions
            valid_suggestions = []
            for s in suggestions:
                if all(k in s for k in ["original_text_snippet", "suggested_revision", "reason_for_change", "change_type", "preserves_intent"]):
                    # Validate change_type
                    if s["change_type"] not in ["clarity", "specificity", "overlap_reduction", "structure"]:
                        s["change_type"] = "clarity"
                    # Validate preserves_intent
                    if s["preserves_intent"] not in ["YES", "POSSIBLY", "NO"]:
                        s["preserves_intent"] = "POSSIBLY"
                    
                    # Find position in original text
                    start_pos = draft_text.find(s["original_text_snippet"])
                    if start_pos >= 0:
                        s["start_position"] = start_pos
                        s["end_position"] = start_pos + len(s["original_text_snippet"])
                    
                    valid_suggestions.append(s)
            
            return {
                "success": True,
                "suggestions": valid_suggestions
            }
            
        except json.JSONDecodeError:
            return {
                "success": False,
                "suggestions": [],
                "error": "Failed to parse LLM response as JSON"
            }
            
    except Exception as e:
        return {
            "success": False,
            "suggestions": [],
            "error": str(e)
        }


def build_overlap_context_from_analysis(analysis: Dict[str, Any]) -> str:
    """
    Build overlap context string from comparative analysis.
    
    Used to inform the LLM about existing overlaps.
    """
    context_parts = []
    
    # Add existing landscape summary
    if analysis.get("existing_landscape"):
        context_parts.append(f"Existing work landscape: {analysis['existing_landscape'][:500]}")
    
    # Add key overlaps
    overlaps = analysis.get("key_overlaps", [])
    if overlaps:
        context_parts.append("Key overlaps with existing work:")
        for overlap in overlaps[:5]:
            if isinstance(overlap, dict):
                concept = overlap.get("concept", "")
                titles = overlap.get("evidence_titles", [])
                context_parts.append(f"- '{concept}' overlaps with: {', '.join(titles[:3])}")
    
    # Add potential differentiators
    diffs = analysis.get("potential_differentiators", [])
    if diffs:
        context_parts.append("Potential differentiating aspects:")
        for diff in diffs[:3]:
            if isinstance(diff, dict):
                aspect = diff.get("aspect", "")
                uncertainty = diff.get("uncertainty", "")
                context_parts.append(f"- {aspect} ({uncertainty})")
    
    return "\n".join(context_parts)


def build_limitations() -> List[str]:
    """
    Build standard limitations for draft suggestions.
    """
    return [
        "These are AI-generated suggestions only, not authoritative improvements.",
        "Suggestions may not fully preserve your original intent - review carefully.",
        "This tool cannot guarantee improved novelty or patentability.",
        "Human expert review is required before finalizing any document.",
        "Some suggestions may not be appropriate for your specific context.",
        "The AI may misunderstand technical nuances in your field."
    ]


DRAFT_DISCLAIMER = """⚠️ DRAFT SUGGESTIONS ONLY
These suggestions are generated by AI for your consideration.
They are NOT guaranteed to improve your document.
Review each suggestion carefully before accepting.
This does NOT constitute legal, technical, or writing advice."""
