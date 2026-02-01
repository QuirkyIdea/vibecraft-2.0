"""
Confidence Calibration Service for Inventix AI - Phase 9

Rule-based confidence calibration to prevent overconfidence.

HARD RULES:
- NEVER HIGH confidence for legal/patent contexts
- Transparent and reversible calibration
- No auto-adjustments that change behavior silently
- Disagreement preserved, not smoothed
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from sqlalchemy.orm import Session

from models import (
    ConfidenceCalibration, ConfidenceLevel, UserFeedback, FeedbackType,
    CandidateEvidence, SimilarityScore, AnalysisState, NoveltyRiskLevel,
    Project, ProjectType
)
from config import get_settings

settings = get_settings()

CALIBRATION_SERVICE_VERSION = "1.0.0"


# ============== Calibration Rules ==============

# Thresholds for confidence determination
EVIDENCE_COUNT_LOW_THRESHOLD = 3
EVIDENCE_COUNT_MEDIUM_THRESHOLD = 10
DISAGREEMENT_HIGH_THRESHOLD = 0.30  # 30%+
SIMILARITY_CLARITY_THRESHOLD = 0.20  # Difference between highest scores

# Contexts that never get HIGH confidence
RESTRICTED_CONTEXTS = {"PATENT", "LEGAL", "MEDICAL", "FINANCIAL"}


# ============== Data Classes ==============

@dataclass
class CalibrationResult:
    """Result of confidence calibration."""
    confidence_level: str
    human_review_recommended: bool
    disagreement_flag: bool
    calibration_notes: List[str]
    metrics: Dict[str, Any]


# ============== Calibration Notes Templates ==============

NOTE_HIGH_DISAGREEMENT = "High disagreement detected on this analysis — exercise caution"
NOTE_LOW_EVIDENCE = "Evidence coverage limited — conclusions may be weak"
NOTE_HUMAN_REVIEW = "Human review strongly recommended before acting"
NOTE_PATENT_CONTEXT = "Patent/legal context — professional review essential"
NOTE_NOVELTY_RED = "High overlap with prior art detected — claims at risk"
NOTE_LOW_SIMILARITY_CLARITY = "Similarity scores lack clear differentiation — interpretation uncertain"
NOTE_NO_FEEDBACK = "No human feedback yet — confidence based on system metrics only"
NOTE_MIXED_SIGNALS = "Mixed evidence signals — additional review advisable"


# ============== Core Functions ==============

def calculate_confidence(
    db: Session,
    project_id: int
) -> CalibrationResult:
    """
    Calculate confidence level for a project based on rule-based calibration.
    
    Rules:
    1. If novelty risk = RED and evidence < 3 → LOW
    2. If disagreement rate > 30% → LOW
    3. If patent/legal context → Never HIGH
    4. If evidence strong + agreement high → MEDIUM
    5. Default → LOW (conservative)
    """
    notes: List[str] = []
    metrics: Dict[str, Any] = {}
    
    # Get project info
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return CalibrationResult(
            confidence_level=ConfidenceLevel.LOW.value,
            human_review_recommended=True,
            disagreement_flag=False,
            calibration_notes=["Project not found"],
            metrics={}
        )
    
    # Check for restricted context
    is_restricted_context = project.type == ProjectType.PATENT
    if is_restricted_context:
        notes.append(NOTE_PATENT_CONTEXT)
    
    # Get evidence count
    evidence_count = db.query(CandidateEvidence).filter(
        CandidateEvidence.project_id == project_id
    ).count()
    metrics["evidence_count"] = evidence_count
    
    if evidence_count < EVIDENCE_COUNT_LOW_THRESHOLD:
        notes.append(NOTE_LOW_EVIDENCE)
    
    # Get novelty risk from analysis state
    analysis_state = db.query(AnalysisState).filter(
        AnalysisState.project_id == project_id
    ).first()
    
    novelty_risk = NoveltyRiskLevel.UNKNOWN
    if analysis_state:
        novelty_risk = analysis_state.novelty_risk
    metrics["novelty_risk"] = novelty_risk.value if novelty_risk else "UNKNOWN"
    
    if novelty_risk == NoveltyRiskLevel.RED:
        notes.append(NOTE_NOVELTY_RED)
    
    # Get feedback stats
    feedback_list = db.query(UserFeedback).filter(
        UserFeedback.project_id == project_id
    ).all()
    
    total_feedback = len(feedback_list)
    metrics["total_feedback"] = total_feedback
    
    if total_feedback == 0:
        notes.append(NOTE_NO_FEEDBACK)
        disagreement_rate = 0.0
    else:
        disagree_types = {FeedbackType.DISAGREE, FeedbackType.NOT_HELPFUL, FeedbackType.NEEDS_REVISION}
        disagreements = sum(1 for f in feedback_list if f.feedback_type in disagree_types)
        disagreement_rate = disagreements / total_feedback
    
    metrics["disagreement_rate"] = round(disagreement_rate, 3)
    
    high_disagreement = disagreement_rate > DISAGREEMENT_HIGH_THRESHOLD
    if high_disagreement:
        notes.append(NOTE_HIGH_DISAGREEMENT)
    
    # Get similarity score clarity
    scores = db.query(SimilarityScore).filter(
        SimilarityScore.project_id == project_id
    ).order_by(SimilarityScore.score.desc()).limit(5).all()
    
    similarity_clarity = 0.0
    if len(scores) >= 2:
        top_score = scores[0].score_float
        second_score = scores[1].score_float
        similarity_clarity = abs(top_score - second_score)
    metrics["similarity_clarity"] = round(similarity_clarity, 3)
    
    if 0 < similarity_clarity < SIMILARITY_CLARITY_THRESHOLD:
        notes.append(NOTE_LOW_SIMILARITY_CLARITY)
    
    # ============== Apply Rules ==============
    
    # Rule 1: RED novelty + low evidence → LOW
    if novelty_risk == NoveltyRiskLevel.RED and evidence_count < EVIDENCE_COUNT_LOW_THRESHOLD:
        confidence_level = ConfidenceLevel.LOW
        notes.append(NOTE_HUMAN_REVIEW)
    
    # Rule 2: High disagreement → LOW
    elif high_disagreement:
        confidence_level = ConfidenceLevel.LOW
        notes.append(NOTE_HUMAN_REVIEW)
    
    # Rule 3: Restricted context → Never HIGH
    elif is_restricted_context:
        # Best case for patent is MEDIUM
        if evidence_count >= EVIDENCE_COUNT_MEDIUM_THRESHOLD and disagreement_rate < 0.1:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW
            notes.append(NOTE_HUMAN_REVIEW)
    
    # Rule 4: Strong evidence + low disagreement → MEDIUM
    elif evidence_count >= EVIDENCE_COUNT_MEDIUM_THRESHOLD and disagreement_rate < 0.1:
        confidence_level = ConfidenceLevel.MEDIUM
    
    # Rule 5: Moderate evidence → LOW-MEDIUM
    elif evidence_count >= EVIDENCE_COUNT_LOW_THRESHOLD:
        if disagreement_rate < 0.2:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW
            notes.append(NOTE_MIXED_SIGNALS)
    
    # Default: Conservative LOW
    else:
        confidence_level = ConfidenceLevel.LOW
        notes.append(NOTE_HUMAN_REVIEW)
    
    # Determine if human review recommended
    human_review_recommended = (
        confidence_level == ConfidenceLevel.LOW or
        is_restricted_context or
        high_disagreement or
        novelty_risk == NoveltyRiskLevel.RED
    )
    
    return CalibrationResult(
        confidence_level=confidence_level.value,
        human_review_recommended=human_review_recommended,
        disagreement_flag=high_disagreement,
        calibration_notes=notes,
        metrics=metrics
    )


def get_or_create_calibration(
    db: Session,
    project_id: int
) -> CalibrationResult:
    """
    Get existing calibration or calculate new one.
    
    Always recalculates to ensure transparency.
    """
    # Always recalculate (no caching that hides changes)
    result = calculate_confidence(db, project_id)
    
    # Update stored calibration
    existing = db.query(ConfidenceCalibration).filter(
        ConfidenceCalibration.project_id == project_id
    ).first()
    
    if existing:
        existing.confidence_level = ConfidenceLevel(result.confidence_level)
        existing.human_review_recommended = result.human_review_recommended
        existing.disagreement_flag = result.disagreement_flag
        existing.calibration_notes = json.dumps(result.calibration_notes)
        existing.total_feedback_count = result.metrics.get("total_feedback", 0)
        existing.disagreement_count = int(result.metrics.get("disagreement_rate", 0) * result.metrics.get("total_feedback", 0))
        existing.evidence_count = result.metrics.get("evidence_count", 0)
    else:
        calibration = ConfidenceCalibration(
            project_id=project_id,
            confidence_level=ConfidenceLevel(result.confidence_level),
            human_review_recommended=result.human_review_recommended,
            disagreement_flag=result.disagreement_flag,
            calibration_notes=json.dumps(result.calibration_notes),
            total_feedback_count=result.metrics.get("total_feedback", 0),
            evidence_count=result.metrics.get("evidence_count", 0)
        )
        db.add(calibration)
    
    db.commit()
    
    return result


def get_confidence_badge(confidence_level: str) -> Dict[str, str]:
    """
    Get display properties for confidence badge.
    
    Used by frontend to render appropriate styling.
    """
    badges = {
        "LOW": {
            "label": "Low Confidence",
            "color": "orange",
            "icon": "⚠️",
            "description": "Results require careful review. Human oversight recommended."
        },
        "MEDIUM": {
            "label": "Medium Confidence",
            "color": "blue", 
            "icon": "ℹ️",
            "description": "Results based on available evidence. Review before acting."
        },
        "HIGH": {
            "label": "High Confidence",
            "color": "green",
            "icon": "✓",
            "description": "Strong evidence support. Standard review sufficient."
        }
    }
    return badges.get(confidence_level, badges["LOW"])
