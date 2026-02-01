"""
Recommendation Service for Inventix AI - Phase 7

Provides venue recommendations based on:
- Topic relevance (keyword matching)
- Novelty risk level (from Phase 4)
- Project type (research/patent)
- Draft maturity

HARD RULES:
- NO prediction of acceptance probability
- NO "good" or "bad" rankings
- NO guarantees of acceptance
- NO misleading confidence language
- All recommendations are SUGGESTIONS only
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from venue_database import (
    Venue, VenueType, VENUES, 
    search_venues, get_venues_by_domain, get_venues_by_type
)
from config import get_settings
import ai_service

settings = get_settings()

RECOMMENDATION_VERSION = "1.0.0"


# ============== Output Types ==============

class ReadinessLevel(str, Enum):
    """Readiness level for submission."""
    WORKSHOP = "WORKSHOP"      # Good for workshops, early feedback
    CONFERENCE = "CONFERENCE"  # Ready for conference submission
    JOURNAL = "JOURNAL"        # Mature enough for journal
    REFINE = "REFINE"          # Needs more work before submission


@dataclass
class VenueRecommendation:
    """Single venue recommendation."""
    name: str
    short_name: str
    venue_type: str
    domains: List[str]
    relevance_reason: str
    submission_formats: List[str]
    match_strength: str  # "strong", "moderate", "weak" - NOT score
    cautions: List[str]  # Specific cautions for this venue


@dataclass
class ReadinessNotes:
    """Assessment of draft readiness."""
    level: ReadinessLevel
    explanation: str
    suggestions: List[str]


@dataclass
class RecommendationResult:
    """Complete recommendation result."""
    success: bool
    venues: List[VenueRecommendation]
    readiness: ReadinessNotes
    general_guidance: List[str]
    limitations: List[str]
    error: Optional[str] = None


# ============== Matching Logic ==============

def compute_keyword_overlap(venue: Venue, keywords: List[str]) -> int:
    """
    Compute overlap score between venue and project keywords.
    
    Returns number of matching keywords (deterministic).
    """
    if not keywords:
        return 0
    
    keywords_lower = [k.lower() for k in keywords]
    
    # Build venue searchable text
    venue_text = (
        venue.name.lower() + " " +
        venue.short_name.lower() + " " +
        venue.scope.lower() + " " +
        " ".join(venue.typical_topics).lower() + " " +
        " ".join(venue.domains).lower()
    )
    
    matches = sum(1 for kw in keywords_lower if kw in venue_text)
    return matches


def determine_match_strength(overlap_count: int, total_keywords: int) -> str:
    """
    Determine qualitative match strength.
    
    NOT a score - just a qualitative label.
    """
    if total_keywords == 0:
        return "weak"
    
    ratio = overlap_count / total_keywords
    
    if ratio >= 0.5:
        return "strong"
    elif ratio >= 0.25:
        return "moderate"
    else:
        return "weak"


def filter_by_novelty_risk(venues: List[Venue], novelty_risk: str) -> List[Venue]:
    """
    Filter venues based on novelty risk level.
    
    Rules:
    - RED: Only workshops and preprints (need refinement)
    - YELLOW: Conferences with caution, avoid flagship journals
    - GREEN: All venues available
    - UNKNOWN: All venues but with uncertainty noted
    """
    if novelty_risk == "RED":
        # Only workshops/preprints for high-risk work
        return [v for v in venues if v.venue_type == VenueType.WORKSHOP or v.tier_hint == "emerging"]
    elif novelty_risk == "YELLOW":
        # Conferences and workshops, but not flagship journals
        return [v for v in venues if v.venue_type != VenueType.JOURNAL or v.tier_hint not in ["flagship"]]
    else:
        # GREEN and UNKNOWN: all venues
        return venues


def filter_by_project_type(venues: List[Venue], project_type: str) -> List[Venue]:
    """
    Filter venues based on project type.
    
    - RESEARCH: All research-focused venues
    - PATENT: Only patent-relevant venues
    - MIXED: All venues
    """
    if project_type == "PATENT":
        return [v for v in venues if v.patent_relevant]
    elif project_type == "RESEARCH":
        return [v for v in venues if v.research_focus]
    else:
        return venues


# ============== Readiness Assessment ==============

def assess_readiness(
    has_draft: bool,
    novelty_risk: str,
    evidence_count: int
) -> ReadinessNotes:
    """
    Assess readiness for submission based on project state.
    
    Returns qualitative readiness level with explanation.
    """
    suggestions = []
    
    # No draft case
    if not has_draft:
        return ReadinessNotes(
            level=ReadinessLevel.REFINE,
            explanation="No draft available. A complete draft is needed before venue selection.",
            suggestions=[
                "Complete a draft of your research/patent document",
                "Run draft optimization (Phase 6) for improvement suggestions",
                "Consider your target audience before finalizing"
            ]
        )
    
    # High risk case
    if novelty_risk == "RED":
        return ReadinessNotes(
            level=ReadinessLevel.WORKSHOP,
            explanation="High overlap detected with existing work. Consider workshops for feedback.",
            suggestions=[
                "Workshop presentation can help refine your contribution",
                "Preprint servers allow early feedback collection",
                "Focus on differentiating aspects before major venue submission",
                "Review comparative analysis (Phase 5) for overlap details"
            ]
        )
    
    # Medium risk case
    if novelty_risk == "YELLOW":
        return ReadinessNotes(
            level=ReadinessLevel.CONFERENCE,
            explanation="Partial overlap detected. Conference submission is appropriate with careful positioning.",
            suggestions=[
                "Clearly articulate what is novel in your submission",
                "Address potential overlap in related work section",
                "Consider targeted conferences in your specific niche",
                "Journal submission may need stronger differentiation"
            ]
        )
    
    # Low risk or unknown
    if novelty_risk == "GREEN":
        if evidence_count >= 5:
            return ReadinessNotes(
                level=ReadinessLevel.JOURNAL,
                explanation="Low overlap and good evidence coverage. Consider both conferences and journals.",
                suggestions=[
                    "Flagship conferences and top journals are appropriate targets",
                    "Ensure thorough experimentation for journal-level work",
                    "Consider the timeline: conferences for faster publication"
                ]
            )
        else:
            return ReadinessNotes(
                level=ReadinessLevel.CONFERENCE,
                explanation="Low overlap detected. Conference submission is recommended.",
                suggestions=[
                    "Good candidate for conference submission",
                    "Retrieve more evidence for comprehensive positioning",
                    "Journal submission may be possible with more validation"
                ]
            )
    
    # UNKNOWN case
    return ReadinessNotes(
        level=ReadinessLevel.WORKSHOP,
        explanation="Insufficient evidence to assess novelty. Start with workshops or preprints.",
        suggestions=[
            "Retrieve more evidence (Phase 3) for better assessment",
            "Compute similarity (Phase 4) before major venue decisions",
            "Workshops provide low-risk feedback opportunity"
        ]
    )


# ============== Main Recommendation Function ==============

def generate_recommendations(
    keywords: List[str],
    project_type: str,
    novelty_risk: str,
    has_draft: bool,
    evidence_count: int,
    domain: Optional[str] = None,
    max_recommendations: int = 10
) -> RecommendationResult:
    """
    Generate venue recommendations based on project characteristics.
    
    This is the main entry point for Phase 7 recommendations.
    
    GUARANTEES:
    - Deterministic: same input → same output
    - No acceptance predictions
    - No numerical rankings
    - All recommendations include limitations
    """
    try:
        # Start with all venues
        candidates = list(VENUES)
        
        # Filter by domain if provided
        if domain:
            domain_matches = get_venues_by_domain(domain)
            if domain_matches:
                candidates = domain_matches
        
        # Filter by project type
        candidates = filter_by_project_type(candidates, project_type)
        
        # Filter by novelty risk
        candidates = filter_by_novelty_risk(candidates, novelty_risk)
        
        # Score by keyword overlap
        scored_venues = []
        for venue in candidates:
            overlap = compute_keyword_overlap(venue, keywords)
            if overlap > 0 or len(keywords) == 0:
                scored_venues.append((venue, overlap))
        
        # Sort by overlap (deterministic)
        scored_venues.sort(key=lambda x: (-x[1], x[0].short_name))
        
        # Take top recommendations
        top_venues = scored_venues[:max_recommendations]
        
        # Build recommendation objects
        recommendations = []
        for venue, overlap in top_venues:
            match_strength = determine_match_strength(overlap, len(keywords))
            
            # Build cautions based on risk
            cautions = []
            if novelty_risk == "RED":
                cautions.append("High overlap risk - use for feedback, not primary publication")
            elif novelty_risk == "YELLOW":
                cautions.append("Partial overlap - clearly position your contribution")
            if novelty_risk == "UNKNOWN":
                cautions.append("Novelty not yet assessed - proceed with caution")
            if not has_draft:
                cautions.append("Complete draft before submission")
            
            # Build relevance reason
            if overlap > 0:
                relevance_reason = f"Topic match based on keywords. Venue scope: {venue.scope[:100]}..."
            else:
                relevance_reason = f"General venue for {', '.join(venue.domains[:3])} research."
            
            recommendations.append(VenueRecommendation(
                name=venue.name,
                short_name=venue.short_name,
                venue_type=venue.venue_type.value,
                domains=venue.domains,
                relevance_reason=relevance_reason,
                submission_formats=venue.submission_formats,
                match_strength=match_strength,
                cautions=cautions
            ))
        
        # Assess readiness
        readiness = assess_readiness(has_draft, novelty_risk, evidence_count)
        
        # Build general guidance
        general_guidance = build_general_guidance(novelty_risk, project_type, has_draft)
        
        # Build limitations (always present)
        limitations = build_limitations()
        
        return RecommendationResult(
            success=True,
            venues=recommendations,
            readiness=readiness,
            general_guidance=general_guidance,
            limitations=limitations
        )
        
    except Exception as e:
        return RecommendationResult(
            success=False,
            venues=[],
            readiness=ReadinessNotes(
                level=ReadinessLevel.REFINE,
                explanation="Error generating recommendations.",
                suggestions=[]
            ),
            general_guidance=[],
            limitations=build_limitations(),
            error=str(e)
        )


def build_general_guidance(novelty_risk: str, project_type: str, has_draft: bool) -> List[str]:
    """Build general guidance notes."""
    guidance = []
    
    if project_type == "PATENT":
        guidance.append("For patent work, prioritize venues that publish applied/industrial research.")
        guidance.append("Consider patent applications in parallel with academic publication.")
    
    if novelty_risk == "RED":
        guidance.append("High overlap detected. Focus on clearly differentiating your work.")
        guidance.append("Workshops provide valuable feedback before major submissions.")
    elif novelty_risk == "YELLOW":
        guidance.append("Address overlapping concepts explicitly in your related work section.")
    elif novelty_risk == "GREEN":
        guidance.append("Low overlap is promising, but ensure thorough experimentation.")
    
    if not has_draft:
        guidance.append("A complete draft helps refine venue selection.")
    
    guidance.append("Check venue deadlines and formatting requirements before submission.")
    
    return guidance


def build_limitations() -> List[str]:
    """Build standard limitations list."""
    return [
        "These are suggestions only, not guarantees of acceptance.",
        "Venue fit depends on many factors not captured here.",
        "Acceptance rates and review processes vary.",
        "This system does not have access to submission deadlines.",
        "Always verify venue requirements before submission.",
        "Consider consulting with advisors or mentors.",
        "No endorsement of any venue is implied."
    ]


# ============== LLM Explanation (Optional) ==============

def generate_explanation_with_llm(
    venue: Venue,
    keywords: List[str],
    novelty_risk: str
) -> str:
    """
    Generate human-readable explanation using LLM.
    
    ONLY for explanation phrasing - does NOT affect ranking.
    
    Falls back to template-based explanation if LLM fails.
    """
    prompt = f"""You are a helpful academic advisor. Generate a brief (1-2 sentences) explanation of why this venue might be suitable for this research.

Venue: {venue.name} ({venue.short_name})
Type: {venue.venue_type.value}
Scope: {venue.scope}
Project keywords: {', '.join(keywords[:5])}
Novelty risk: {novelty_risk}

RULES:
- Do NOT predict acceptance
- Do NOT claim the venue is "good" or "best"
- Do NOT guarantee anything
- Use phrases like "may be suitable", "could consider", "worth exploring"

Generate a brief, honest explanation:"""

    try:
        result = ai_service.call_llm(prompt, max_tokens=100)
        if result.get("success"):
            return result.get("output", "")
    except:
        pass
    
    # Fallback to template
    return f"{venue.short_name} publishes research on {', '.join(venue.typical_topics[:3])}."


RECOMMENDATION_DISCLAIMER = """⚠️ VENUE SUGGESTIONS ONLY

These recommendations are generated based on topic matching and project characteristics.
They do NOT guarantee acceptance or predict review outcomes.

Consider:
- Checking submission deadlines
- Reviewing venue requirements
- Consulting with advisors
- Assessing your work's fit with venue scope

This is guidance, not a guarantee."""
