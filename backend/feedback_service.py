"""
Feedback Service for Inventix AI - Phase 9

Captures and manages human feedback on AI outputs.

HARD RULES:
- NEVER alter original AI outputs
- NEVER overwrite human feedback
- Preserve disagreement - no smoothing
- Full audit trail
"""
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from models import UserFeedback, FeedbackType, OutputType
from config import get_settings

settings = get_settings()

FEEDBACK_SERVICE_VERSION = "1.0.0"


# ============== Data Classes ==============

@dataclass
class FeedbackSubmission:
    """Feedback submission result."""
    success: bool
    feedback_id: int
    output_id: str
    feedback_type: str
    message: str
    timestamp: str


@dataclass
class FeedbackSummary:
    """Aggregated feedback summary."""
    output_id: str
    total_count: int
    helpful_count: int
    not_helpful_count: int
    agree_count: int
    disagree_count: int
    needs_revision_count: int
    needs_expert_count: int
    disagreement_rate: float  # 0.0 - 1.0
    comments: List[str]


@dataclass  
class ProjectFeedbackStats:
    """Project-level feedback statistics."""
    project_id: int
    total_feedback: int
    total_outputs_rated: int
    overall_disagreement_rate: float
    outputs_needing_review: int
    recent_feedback: List[Dict[str, Any]]


# ============== Helper Functions ==============

def hash_ip(ip_address: Optional[str]) -> Optional[str]:
    """Hash IP address for abuse prevention without storing raw IP."""
    if not ip_address:
        return None
    return hashlib.sha256(ip_address.encode()).hexdigest()[:32]


def calculate_disagreement_rate(
    disagree_count: int,
    agree_count: int,
    not_helpful_count: int,
    helpful_count: int
) -> float:
    """Calculate disagreement rate from feedback counts."""
    total_positive = agree_count + helpful_count
    total_negative = disagree_count + not_helpful_count
    total = total_positive + total_negative
    
    if total == 0:
        return 0.0
    
    return round(total_negative / total, 3)


# ============== Core Functions ==============

def submit_feedback(
    db: Session,
    output_id: str,
    output_type: str,
    project_id: int,
    feedback_type: str,
    user_id: Optional[str] = None,
    user_role: Optional[str] = None,
    comment: Optional[str] = None,
    ip_address: Optional[str] = None
) -> FeedbackSubmission:
    """
    Submit feedback on an AI output.
    
    NEVER alters the original AI output.
    Just stores the feedback for audit and calibration.
    """
    try:
        # Validate feedback type
        try:
            fb_type = FeedbackType(feedback_type)
        except ValueError:
            return FeedbackSubmission(
                success=False,
                feedback_id=0,
                output_id=output_id,
                feedback_type=feedback_type,
                message=f"Invalid feedback type: {feedback_type}",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Validate output type
        try:
            out_type = OutputType(output_type)
        except ValueError:
            return FeedbackSubmission(
                success=False,
                feedback_id=0,
                output_id=output_id,
                feedback_type=feedback_type,
                message=f"Invalid output type: {output_type}",
                timestamp=datetime.utcnow().isoformat()
            )
        
        # Create feedback record
        feedback = UserFeedback(
            output_id=output_id,
            output_type=out_type,
            project_id=project_id,
            user_id=user_id,
            user_role=user_role,
            feedback_type=fb_type,
            comment=comment,
            ip_hash=hash_ip(ip_address)
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return FeedbackSubmission(
            success=True,
            feedback_id=feedback.id,
            output_id=output_id,
            feedback_type=feedback_type,
            message="Feedback recorded successfully. Thank you for helping improve the system.",
            timestamp=feedback.created_at.isoformat()
        )
        
    except Exception as e:
        db.rollback()
        return FeedbackSubmission(
            success=False,
            feedback_id=0,
            output_id=output_id,
            feedback_type=feedback_type,
            message=f"Failed to record feedback: {str(e)}",
            timestamp=datetime.utcnow().isoformat()
        )


def get_feedback_for_output(
    db: Session,
    output_id: str
) -> FeedbackSummary:
    """
    Get all feedback for a specific output.
    
    Returns aggregated summary with counts and comments.
    """
    feedback_list = db.query(UserFeedback).filter(
        UserFeedback.output_id == output_id
    ).order_by(UserFeedback.created_at.desc()).all()
    
    helpful = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.HELPFUL)
    not_helpful = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.NOT_HELPFUL)
    agree = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.AGREE)
    disagree = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.DISAGREE)
    needs_revision = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.NEEDS_REVISION)
    needs_expert = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.NEEDS_EXPERT)
    
    comments = [f.comment for f in feedback_list if f.comment]
    
    return FeedbackSummary(
        output_id=output_id,
        total_count=len(feedback_list),
        helpful_count=helpful,
        not_helpful_count=not_helpful,
        agree_count=agree,
        disagree_count=disagree,
        needs_revision_count=needs_revision,
        needs_expert_count=needs_expert,
        disagreement_rate=calculate_disagreement_rate(disagree, agree, not_helpful, helpful),
        comments=comments[:10]  # Limit to most recent 10
    )


def get_project_feedback(
    db: Session,
    project_id: int
) -> ProjectFeedbackStats:
    """
    Get all feedback for a project.
    
    Returns project-level statistics and recent feedback.
    """
    feedback_list = db.query(UserFeedback).filter(
        UserFeedback.project_id == project_id
    ).order_by(UserFeedback.created_at.desc()).all()
    
    # Unique outputs rated
    unique_outputs = set(f.output_id for f in feedback_list)
    
    # Count disagreements
    disagree_types = {FeedbackType.DISAGREE, FeedbackType.NOT_HELPFUL, FeedbackType.NEEDS_REVISION}
    disagreements = sum(1 for f in feedback_list if f.feedback_type in disagree_types)
    
    # Disagreement rate
    disagreement_rate = disagreements / len(feedback_list) if feedback_list else 0.0
    
    # Outputs needing review
    needs_review = sum(1 for f in feedback_list if f.feedback_type == FeedbackType.NEEDS_EXPERT)
    
    # Recent feedback (last 10)
    recent = [
        {
            "id": f.id,
            "output_id": f.output_id,
            "output_type": f.output_type.value,
            "feedback_type": f.feedback_type.value,
            "comment": f.comment,
            "timestamp": f.created_at.isoformat()
        }
        for f in feedback_list[:10]
    ]
    
    return ProjectFeedbackStats(
        project_id=project_id,
        total_feedback=len(feedback_list),
        total_outputs_rated=len(unique_outputs),
        overall_disagreement_rate=round(disagreement_rate, 3),
        outputs_needing_review=needs_review,
        recent_feedback=recent
    )
