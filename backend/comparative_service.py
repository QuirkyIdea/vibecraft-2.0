"""
Comparative Summarization Service for Inventix AI - Phase 5

Generates evidence-grounded comparative analysis explaining novelty.

CRITICAL RULES:
- Summaries MUST be grounded in retrieved evidence only
- LLM must NEVER invent prior work
- Every statement traces to specific evidence
- Uncertainty language is REQUIRED
- No legal conclusions or patentability claims
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from config import get_settings
import ai_service

settings = get_settings()


# ============== Output Schemas ==============

class EvidenceSummary(BaseModel):
    """Summary of a single evidence document"""
    evidence_id: int
    title: str
    source: str
    source_url: str
    summary: str


class OverlapItem(BaseModel):
    """Single overlap point between idea and evidence"""
    idea_concept: str
    evidence_concept: str
    evidence_id: int
    evidence_title: str


class DifferenceItem(BaseModel):
    """Single difference point with uncertainty"""
    aspect: str
    description: str
    uncertainty: str  # Required uncertainty language


class ComparativeOutput(BaseModel):
    """Complete structured comparative analysis"""
    existing_work_summaries: List[EvidenceSummary]
    overlap_analysis: List[OverlapItem]
    differentiation_analysis: List[DifferenceItem]
    novelty_explanation: str
    limitations: List[str]
    confidence_notes: str
    generated_at: str


# ============== Prompt Templates ==============

COMPARATIVE_PROMPT_TEMPLATE = """You are an evidence-based research analyst. Your task is to compare a user's idea against existing work.

CRITICAL RULES (MANDATORY):
1. Do NOT invent or hallucinate any prior work
2. Only reference the evidence provided below
3. Use uncertainty language: "appears to", "seems to", "no direct mention found"
4. Quote or paraphrase the evidence cautiously
5. Never claim legal patentability or academic novelty
6. Be honest about what you don't know

---

USER'S IDEA:
{idea_text}

---

EVIDENCE DOCUMENT:
Title: {evidence_title}
Source: {evidence_source}
Abstract/Content: {evidence_abstract}

SIMILARITY SCORE: {similarity_score:.2f}
NOVELTY RISK: {novelty_risk}

---

Based ONLY on the evidence above, provide:

1. EXISTING WORK SUMMARY (2-3 sentences):
What does this evidence document describe? Summarize its main contribution.

2. OVERLAP ANALYSIS (bullet points):
What concepts or approaches appear in BOTH the user's idea AND the evidence?
Format: "User's [concept] overlaps with evidence's [concept]"

3. DIFFERENTIATION ANALYSIS (bullet points):
What aspects of the user's idea appear different from the evidence?
MUST include uncertainty language. 
Format: "Appears to differ in [aspect]: [description]. (Uncertainty: [statement])"

4. NOVELTY EXPLANATION (paragraph):
Explain why the similarity score is {novelty_risk}. What drives the overlap or difference?

5. LIMITATIONS:
- What aspects of the user's idea could not be compared?
- What evidence might be missing?
- What requires human expert verification?

Respond in the following JSON format only:
{{
  "existing_work_summary": "...",
  "overlap_points": [
    {{"idea_concept": "...", "evidence_concept": "..."}}
  ],
  "difference_points": [
    {{"aspect": "...", "description": "...", "uncertainty": "..."}}
  ],
  "novelty_explanation": "...",
  "limitations": ["...", "..."]
}}"""


MULTI_EVIDENCE_PROMPT = """You are an evidence-based research analyst. Compare a user's idea against multiple evidence documents.

CRITICAL RULES:
1. Do NOT invent or hallucinate any prior work
2. Only reference the evidence provided below
3. Use uncertainty language throughout
4. Reference specific evidence by title when making claims
5. Be honest about limitations

---

USER'S IDEA:
{idea_text}

---

EVIDENCE DOCUMENTS:

{evidence_list}

---

OVERALL NOVELTY: {overall_risk}
MAX SIMILARITY: {max_similarity:.2f}

---

Provide a comprehensive comparative analysis:

1. EXISTING LANDSCAPE: What does the current evidence suggest exists in this space?

2. KEY OVERLAPS: What shared concepts appear across user's idea and evidence?
   Reference specific evidence by title.

3. POTENTIAL DIFFERENTIATORS: What aspects of the user's idea may be novel?
   Use uncertainty language. Be specific about which evidence lacks these concepts.

4. RISK EXPLANATION: Why is the novelty risk {overall_risk}?

5. CONFIDENCE & LIMITATIONS:
   - Coverage gaps
   - Need for additional search
   - Recommendation for expert review

Respond in JSON format:
{{
  "existing_landscape": "...",
  "key_overlaps": [{{"concept": "...", "evidence_titles": ["..."]}}],
  "potential_differentiators": [{{"aspect": "...", "description": "...", "uncertainty": "..."}}],
  "risk_explanation": "...",
  "limitations": ["..."],
  "confidence_level": "low|medium|high",
  "recommendation": "..."
}}"""


# ============== Service Functions ==============

def generate_single_comparison(
    idea_text: str,
    evidence_id: int,
    evidence_title: str,
    evidence_source: str,
    evidence_abstract: str,
    similarity_score: float,
    novelty_risk: str
) -> Dict[str, Any]:
    """
    Generate comparative analysis for a single evidence document.
    
    Returns structured output with evidence-grounded claims.
    """
    prompt = COMPARATIVE_PROMPT_TEMPLATE.format(
        idea_text=idea_text[:2000],
        evidence_title=evidence_title,
        evidence_source=evidence_source,
        evidence_abstract=evidence_abstract[:1500],
        similarity_score=similarity_score,
        novelty_risk=novelty_risk
    )
    
    try:
        response = ai_service.call_llm(prompt, max_tokens=1500)
        
        if not response["success"]:
            return {
                "success": False,
                "error": response.get("error", "LLM call failed")
            }
        
        # Parse JSON response
        ai_output = response["output"]
        
        # Try to extract JSON from response
        try:
            # Handle potential markdown code blocks
            if "```json" in ai_output:
                json_str = ai_output.split("```json")[1].split("```")[0]
            elif "```" in ai_output:
                json_str = ai_output.split("```")[1].split("```")[0]
            else:
                json_str = ai_output
            
            parsed = json.loads(json_str.strip())
            parsed["success"] = True
            parsed["evidence_id"] = evidence_id
            parsed["evidence_title"] = evidence_title
            return parsed
            
        except json.JSONDecodeError:
            # Return raw output if JSON parsing fails
            return {
                "success": True,
                "evidence_id": evidence_id,
                "evidence_title": evidence_title,
                "raw_output": ai_output,
                "parse_error": "Could not parse as JSON"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_multi_evidence_comparison(
    idea_text: str,
    evidence_items: List[Dict[str, Any]],
    overall_risk: str,
    max_similarity: float
) -> Dict[str, Any]:
    """
    Generate comparative analysis across multiple evidence documents.
    
    Provides holistic view of novelty landscape.
    """
    # Build evidence list string
    evidence_list = ""
    for i, ev in enumerate(evidence_items, 1):
        evidence_list += f"""
--- Evidence {i} ---
Title: {ev['title']}
Source: {ev['source']}
Similarity: {ev['similarity']:.2f}
Abstract: {ev['abstract'][:800]}
"""
    
    prompt = MULTI_EVIDENCE_PROMPT.format(
        idea_text=idea_text[:2000],
        evidence_list=evidence_list,
        overall_risk=overall_risk,
        max_similarity=max_similarity
    )
    
    try:
        response = ai_service.call_llm(prompt, max_tokens=2000)
        
        if not response["success"]:
            return {
                "success": False,
                "error": response.get("error", "LLM call failed")
            }
        
        ai_output = response["output"]
        
        try:
            if "```json" in ai_output:
                json_str = ai_output.split("```json")[1].split("```")[0]
            elif "```" in ai_output:
                json_str = ai_output.split("```")[1].split("```")[0]
            else:
                json_str = ai_output
            
            parsed = json.loads(json_str.strip())
            parsed["success"] = True
            parsed["evidence_count"] = len(evidence_items)
            return parsed
            
        except json.JSONDecodeError:
            return {
                "success": True,
                "evidence_count": len(evidence_items),
                "raw_output": ai_output,
                "parse_error": "Could not parse as JSON"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def build_limitations_section(
    evidence_count: int,
    research_count: int,
    patent_count: int,
    max_similarity: float
) -> List[str]:
    """
    Build explicit limitations section.
    
    Always honest about coverage gaps.
    """
    limitations = []
    
    if evidence_count < 5:
        limitations.append(
            f"Analysis based on limited evidence ({evidence_count} documents). "
            "Additional prior art may exist."
        )
    
    if patent_count == 0:
        limitations.append(
            "No patent documents were compared. Patent landscape may differ from research landscape."
        )
    
    if research_count == 0:
        limitations.append(
            "No research papers were compared. Academic prior art may exist."
        )
    
    if max_similarity < 0.5:
        limitations.append(
            "Low similarity scores may indicate novel territory OR insufficient evidence coverage."
        )
    
    limitations.append(
        "This analysis does not constitute legal advice. "
        "Human expert review is required for patent or publication decisions."
    )
    
    limitations.append(
        "Evidence retrieval may not cover all relevant databases or recent publications."
    )
    
    return limitations
