"""
Claim Structuring Service for Inventix AI - Phase 8

Helps inventors structure ideas into patent-style claim hierarchies.

⚠️ STRUCTURAL INTELLIGENCE ONLY - NOT LEGAL ADVICE ⚠️

HARD RULES:
- DO NOT claim "this claim is patentable"
- DO NOT generate filing-ready claims
- DO NOT replace patent attorneys
- DO NOT hide uncertainty
- Every output includes legal disclaimer
"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

import ai_service
from config import get_settings

settings = get_settings()

CLAIM_SERVICE_VERSION = "1.0.0"
PROMPT_VERSION = "1.0"


# ============== Legal Disclaimer (ALWAYS PRESENT) ==============

LEGAL_DISCLAIMER = """⚠️ CONCEPTUAL DRAFT – NOT LEGAL ADVICE

This claim structure is a CONCEPTUAL DRAFT only. It is NOT:
- A filed patent claim
- A guarantee of patentability
- Legal advice of any kind
- A replacement for patent attorney review

IMPORTANT:
- Consult a registered patent attorney before filing
- Patent claim drafting requires professional expertise
- This tool provides STRUCTURAL assistance only
- All claims require professional review and revision

This is an educational aid, not a legal document."""


ATTORNEY_HANDOFF_TEMPLATE = """## Attorney Handoff Notes

### Claims Generated
- Independent claims: {independent_count}
- Dependent claims: {dependent_count}

### Suggested Questions for Patent Counsel
1. Are the independent claims appropriately scoped for the intended protection?
2. Do the dependent claims adequately narrow for fallback positions?
3. Are there additional claim types (method, system, apparatus) that should be drafted?
4. Does the claim language properly capture the technical innovation?
5. Are there priority date or prior art concerns to address?

### Areas Requiring Professional Review
{review_areas}

### Prior Art Context
{prior_art_notes}

### Novelty Risk Assessment
- Risk Level: {novelty_risk}
- Recommendation: {risk_recommendation}
"""


# ============== LLM Prompts ==============

CLAIM_GENERATION_PROMPT = """You are a patent claim structuring assistant. Help structure the technical idea into a patent-style claim hierarchy.

CRITICAL RULES:
- This is a CONCEPTUAL DRAFT for educational purposes
- DO NOT assert patentability
- DO NOT claim legal validity
- Mark uncertainty where it exists
- Use patent-style language but note it is not final

TECHNICAL IDEA:
{idea_text}

PRIOR ART CONTEXT (if available):
{overlap_context}

NOVELTY RISK LEVEL: {novelty_risk}

Generate a claim structure with:
1. ONE independent claim that captures the core innovation
2. 2-4 dependent claims that narrow specific aspects
3. For each claim, explain what technical feature it covers

OUTPUT FORMAT (JSON):
{{
  "claims": [
    {{
      "claim_number": 1,
      "claim_type": "INDEPENDENT",
      "claim_text": "A [type] comprising: [elements]...",
      "technical_feature": "What this claim covers",
      "explanation": "Why structured this way",
      "parent_claim_number": null
    }},
    {{
      "claim_number": 2,
      "claim_type": "DEPENDENT",
      "claim_text": "The [type] of claim 1, wherein...",
      "technical_feature": "Specific narrowing aspect",
      "explanation": "Why this is a separate dependent claim",
      "parent_claim_number": 1
    }}
  ],
  "risks": [
    {{
      "claim_number": 1,
      "risk_type": "BROAD",
      "description": "This claim may be considered broad because..."
    }}
  ],
  "review_areas": [
    "Area requiring professional review"
  ]
}}

Generate the claim structure now:"""


NO_CONTEXT_PROMPT = """You are a patent claim structuring assistant. Help structure the technical idea into a patent-style claim hierarchy.

CRITICAL RULES:
- This is a CONCEPTUAL DRAFT for educational purposes
- DO NOT assert patentability
- DO NOT claim legal validity
- Mark uncertainty where it exists
- Use patent-style language but note it is not final

TECHNICAL IDEA:
{idea_text}

NOTE: No prior art analysis has been performed yet. Claims may need significant revision after prior art review.

Generate a claim structure with:
1. ONE independent claim that captures the core innovation
2. 2-4 dependent claims that narrow specific aspects
3. For each claim, explain what technical feature it covers

OUTPUT FORMAT (JSON):
{{
  "claims": [
    {{
      "claim_number": 1,
      "claim_type": "INDEPENDENT",
      "claim_text": "A [type] comprising: [elements]...",
      "technical_feature": "What this claim covers",
      "explanation": "Why structured this way",
      "parent_claim_number": null
    }},
    {{
      "claim_number": 2,
      "claim_type": "DEPENDENT",
      "claim_text": "The [type] of claim 1, wherein...",
      "technical_feature": "Specific narrowing aspect",
      "explanation": "Why this is a separate dependent claim",
      "parent_claim_number": 1
    }}
  ],
  "risks": [
    {{
      "claim_number": 1,
      "risk_type": "BROAD",
      "description": "Without prior art analysis, claim breadth cannot be assessed"
    }}
  ],
  "review_areas": [
    "Prior art search required",
    "Professional claim drafting needed"
  ]
}}

Generate the claim structure now:"""


# ============== Data Classes ==============

@dataclass
class ClaimItem:
    """Single claim in the hierarchy."""
    claim_number: int
    claim_type: str  # INDEPENDENT or DEPENDENT
    claim_text: str
    technical_feature: str
    explanation: str
    parent_claim_number: Optional[int]


@dataclass
class RiskItem:
    """Risk annotation for a claim."""
    claim_number: int
    risk_type: str  # BROAD, OVERLAP, NEEDS_NARROWING
    description: str
    evidence_id: Optional[int] = None


@dataclass
class ClaimGenerationResult:
    """Complete claim generation result."""
    success: bool
    claims: List[ClaimItem]
    risks: List[RiskItem]
    review_areas: List[str]
    attorney_handoff: str
    disclaimer: str
    input_hash: str
    error: Optional[str] = None


# ============== Helper Functions ==============

def compute_input_hash(idea_text: str, overlap_context: str, novelty_risk: str) -> str:
    """Compute SHA256 hash of inputs for auditing."""
    content = f"{idea_text}|{overlap_context}|{novelty_risk}"
    return hashlib.sha256(content.encode()).hexdigest()


def build_overlap_context(comparative_analysis: Optional[Dict]) -> str:
    """Build overlap context string from comparative analysis."""
    if not comparative_analysis:
        return "No prior art analysis available."
    
    context_parts = []
    
    if comparative_analysis.get("existing_work_summary"):
        context_parts.append(f"Existing Work: {comparative_analysis['existing_work_summary'][:500]}")
    
    overlaps = comparative_analysis.get("overlaps", [])
    if overlaps:
        context_parts.append("Key Overlaps with Prior Art:")
        for i, o in enumerate(overlaps[:3]):
            if isinstance(o, dict):
                context_parts.append(f"  {i+1}. {o.get('description', str(o)[:200])}")
            else:
                context_parts.append(f"  {i+1}. {str(o)[:200]}")
    
    diffs = comparative_analysis.get("differentiators", [])
    if diffs:
        context_parts.append("Potential Differentiators:")
        for i, d in enumerate(diffs[:3]):
            if isinstance(d, dict):
                context_parts.append(f"  {i+1}. {d.get('description', str(d)[:200])}")
            else:
                context_parts.append(f"  {i+1}. {str(d)[:200]}")
    
    return "\n".join(context_parts) if context_parts else "No prior art analysis available."


def get_risk_recommendation(novelty_risk: str) -> str:
    """Get recommendation based on novelty risk level."""
    recommendations = {
        "GREEN": "Low overlap detected. Consider broad claims but verify with patent counsel.",
        "YELLOW": "Moderate overlap. Focus on differentiating aspects in claims. Attorney review essential.",
        "RED": "High overlap with prior art. Claims may need significant narrowing. Consult attorney before proceeding.",
        "UNKNOWN": "Prior art analysis not performed. Complete evidence retrieval and similarity analysis first."
    }
    return recommendations.get(novelty_risk, recommendations["UNKNOWN"])


# ============== Main Generation Function ==============

def generate_claim_structure(
    idea_text: str,
    overlap_context: Optional[str] = None,
    novelty_risk: str = "UNKNOWN",
    evidence_ids: Optional[List[int]] = None
) -> ClaimGenerationResult:
    """
    Generate patent claim structure from idea text.
    
    Returns conceptual claims with:
    - Claim hierarchy (independent + dependent)
    - Risk annotations
    - Attorney handoff notes
    - Legal disclaimer
    
    NEVER asserts patentability.
    """
    # Truncate idea if too long
    idea_text = idea_text[:8000]
    
    # Compute input hash for auditing
    input_hash = compute_input_hash(idea_text, overlap_context or "", novelty_risk)
    
    # Choose prompt based on context availability
    if overlap_context and overlap_context != "No prior art analysis available.":
        prompt = CLAIM_GENERATION_PROMPT.format(
            idea_text=idea_text,
            overlap_context=overlap_context[:2000],
            novelty_risk=novelty_risk
        )
    else:
        prompt = NO_CONTEXT_PROMPT.format(idea_text=idea_text)
    
    try:
        # Build system prompt
        system_prompt = """You are a patent claim structuring assistant. 
You help inventors structure technical ideas into patent-style claim hierarchies.
This is for educational purposes ONLY - NOT legal advice.
DO NOT assert patentability or legal validity.
Always output valid JSON."""
        
        # Call LLM with correct signature
        response = ai_service.call_llm(
            system_prompt=system_prompt,
            user_message=prompt,
            prompt_version=PROMPT_VERSION
        )
        
        if not response.success:
            return ClaimGenerationResult(
                success=False,
                claims=[],
                risks=[],
                review_areas=[],
                attorney_handoff="",
                disclaimer=LEGAL_DISCLAIMER,
                input_hash=input_hash,
                error=response.error or "LLM call failed"
            )
        
        # Parse JSON response
        ai_output = response.ai_output or ""

        
        try:
            # Handle markdown code blocks
            if "```json" in ai_output:
                json_str = ai_output.split("```json")[1].split("```")[0]
            elif "```" in ai_output:
                json_str = ai_output.split("```")[1].split("```")[0]
            else:
                json_str = ai_output
            
            parsed = json.loads(json_str.strip())
            
            # Extract claims
            claims = []
            for c in parsed.get("claims", []):
                claims.append(ClaimItem(
                    claim_number=c.get("claim_number", len(claims) + 1),
                    claim_type=c.get("claim_type", "DEPENDENT"),
                    claim_text=c.get("claim_text", ""),
                    technical_feature=c.get("technical_feature", ""),
                    explanation=c.get("explanation", ""),
                    parent_claim_number=c.get("parent_claim_number")
                ))
            
            # Extract risks
            risks = []
            for r in parsed.get("risks", []):
                risk_type = r.get("risk_type", "BROAD")
                if risk_type not in ["BROAD", "OVERLAP", "NEEDS_NARROWING"]:
                    risk_type = "BROAD"
                
                risks.append(RiskItem(
                    claim_number=r.get("claim_number", 1),
                    risk_type=risk_type,
                    description=r.get("description", "")
                ))
            
            # Extract review areas
            review_areas = parsed.get("review_areas", [
                "Professional patent attorney review required",
                "Prior art search validation needed"
            ])
            
            # Build attorney handoff
            independent_count = sum(1 for c in claims if c.claim_type == "INDEPENDENT")
            dependent_count = sum(1 for c in claims if c.claim_type == "DEPENDENT")
            
            attorney_handoff = ATTORNEY_HANDOFF_TEMPLATE.format(
                independent_count=independent_count,
                dependent_count=dependent_count,
                review_areas="\n".join(f"- {area}" for area in review_areas),
                prior_art_notes=overlap_context[:500] if overlap_context else "Prior art analysis not performed.",
                novelty_risk=novelty_risk,
                risk_recommendation=get_risk_recommendation(novelty_risk)
            )
            
            return ClaimGenerationResult(
                success=True,
                claims=claims,
                risks=risks,
                review_areas=review_areas,
                attorney_handoff=attorney_handoff,
                disclaimer=LEGAL_DISCLAIMER,
                input_hash=input_hash
            )
            
        except json.JSONDecodeError as e:
            return ClaimGenerationResult(
                success=False,
                claims=[],
                risks=[],
                review_areas=[],
                attorney_handoff="",
                disclaimer=LEGAL_DISCLAIMER,
                input_hash=input_hash,
                error=f"Failed to parse LLM response: {str(e)}"
            )
            
    except Exception as e:
        return ClaimGenerationResult(
            success=False,
            claims=[],
            risks=[],
            review_areas=[],
            attorney_handoff="",
            disclaimer=LEGAL_DISCLAIMER,
            input_hash=input_hash,
            error=str(e)
        )


def build_dependency_graph(claims: List[ClaimItem]) -> Dict[str, Any]:
    """
    Build a visualization-ready dependency graph from claims.
    
    Returns:
    {
        "nodes": [{"id": 1, "label": "Claim 1", "type": "INDEPENDENT"}],
        "edges": [{"from": 1, "to": 2, "label": "depends on"}]
    }
    """
    nodes = []
    edges = []
    
    for claim in claims:
        nodes.append({
            "id": claim.claim_number,
            "label": f"Claim {claim.claim_number}",
            "type": claim.claim_type,
            "text_preview": claim.claim_text[:100] + "..." if len(claim.claim_text) > 100 else claim.claim_text
        })
        
        if claim.parent_claim_number is not None:
            edges.append({
                "from": claim.parent_claim_number,
                "to": claim.claim_number,
                "label": "depends on"
            })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "root_claims": [c.claim_number for c in claims if c.claim_type == "INDEPENDENT"]
    }
