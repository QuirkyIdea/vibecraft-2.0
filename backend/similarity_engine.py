"""
Similarity Engine for Inventix AI - Phase 4

Computes deterministic, reproducible similarity scores between texts.
Uses cosine similarity on embeddings.

Rules:
- Similarity MUST be computed from real text
- Every score MUST link to specific evidence
- No LLM-only similarity judgments
- No random or heuristic-only scoring
- Same input → same score every time
"""
import math
from typing import List, Optional, Tuple
from enum import Enum as PyEnum
from pydantic import BaseModel
from config import get_settings

settings = get_settings()


class NoveltyRisk(str, PyEnum):
    """Novelty risk classification"""
    GREEN = "GREEN"      # Low overlap - likely novel
    YELLOW = "YELLOW"    # Partial overlap - needs review
    RED = "RED"          # High overlap - significant concern
    UNKNOWN = "UNKNOWN"  # Insufficient evidence


class SimilarityResult(BaseModel):
    """Result of similarity computation for one evidence item"""
    evidence_id: int
    evidence_title: str
    evidence_type: str  # "paper" or "patent"
    source_url: str
    similarity_score: float  # 0.0 - 1.0
    

class NoveltyRiskResult(BaseModel):
    """Complete novelty risk assessment"""
    project_id: int
    novelty_risk: NoveltyRisk
    max_similarity_score: Optional[float]
    top_match: Optional[SimilarityResult]
    research_risk: NoveltyRisk
    research_max_score: Optional[float]
    patent_risk: NoveltyRisk
    patent_max_score: Optional[float]
    total_evidence_compared: int
    explanation: Optional[str] = None
    notes: str


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Returns value between -1.0 and 1.0.
    Normalized to 0.0 - 1.0 for our use case.
    
    This is a DETERMINISTIC function:
    - Same inputs → same output
    - No randomness
    """
    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vector dimensions must match: {len(vec_a)} vs {len(vec_b)}")
    
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    similarity = dot_product / (norm_a * norm_b)
    
    # Normalize from [-1, 1] to [0, 1]
    # In practice, text embeddings rarely go negative
    return max(0.0, min(1.0, (similarity + 1) / 2))


def classify_novelty_risk(
    similarity_score: float,
    evidence_type: str
) -> NoveltyRisk:
    """
    Classify novelty risk based on similarity score.
    
    Uses CONFIGURABLE, DOCUMENTED thresholds.
    Patent thresholds are STRICTER than research.
    """
    if evidence_type == "patent":
        red_threshold = settings.patent_red_threshold
        yellow_threshold = settings.patent_yellow_threshold
    else:  # research paper
        red_threshold = settings.research_red_threshold
        yellow_threshold = settings.research_yellow_threshold
    
    if similarity_score >= red_threshold:
        return NoveltyRisk.RED
    elif similarity_score >= yellow_threshold:
        return NoveltyRisk.YELLOW
    else:
        return NoveltyRisk.GREEN


def compute_overall_risk(
    research_scores: List[float],
    patent_scores: List[float]
) -> Tuple[NoveltyRisk, Optional[float], str]:
    """
    Compute overall novelty risk from all similarity scores.
    
    Rules:
    - Risk is based on MAX similarity score
    - Patent risk takes precedence if RED
    - Returns UNKNOWN if no evidence
    """
    all_scores = []
    
    # Get max research score
    research_max = max(research_scores) if research_scores else None
    patent_max = max(patent_scores) if patent_scores else None
    
    if research_max is not None:
        all_scores.append(("research", research_max))
    if patent_max is not None:
        all_scores.append(("patent", patent_max))
    
    if not all_scores:
        return NoveltyRisk.UNKNOWN, None, "Insufficient evidence to assess novelty risk."
    
    # Find max score and its type
    max_type, max_score = max(all_scores, key=lambda x: x[1])
    
    # Classify based on max
    risk = classify_novelty_risk(max_score, max_type)
    
    # Generate explanation
    if risk == NoveltyRisk.RED:
        notes = f"High similarity detected ({max_score:.2f}) with {max_type}. Significant overlap with existing work."
    elif risk == NoveltyRisk.YELLOW:
        notes = f"Moderate similarity detected ({max_score:.2f}) with {max_type}. Partial overlap - review recommended."
    else:
        notes = f"Low similarity detected ({max_score:.2f}). Idea appears to have novel aspects."
    
    return risk, max_score, notes


def create_explanation_prompt(
    idea_text: str,
    evidence_title: str,
    evidence_abstract: str,
    similarity_score: float,
    novelty_risk: NoveltyRisk
) -> str:
    """
    Create prompt for LLM to explain similarity result.
    
    LLM is used ONLY to explain - NOT to score.
    The numeric score and classification are FIXED.
    """
    return f"""Explain why the following two texts have a similarity score of {similarity_score:.2f}, which resulted in a {novelty_risk.value} novelty risk classification.

USER'S IDEA:
{idea_text[:1000]}

SIMILAR EXISTING WORK:
Title: {evidence_title}
Abstract: {evidence_abstract[:1000]}

SIMILARITY SCORE: {similarity_score:.2f}
CLASSIFICATION: {novelty_risk.value}

RULES:
- Do NOT change the classification or score
- Explain what concepts or phrases are shared
- Be specific about overlapping technical elements
- Keep explanation under 200 words
- Do NOT make legal claims

Provide a brief, factual explanation of the similarity."""
