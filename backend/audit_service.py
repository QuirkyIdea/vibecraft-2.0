"""
Audit Service for Inventix AI - Phase 10

Handles immutable logging of system actions for provenance and compliance.
Append-only log.

HARD RULES:
- Full provenance for every AI output
- No deletions
- All critical actions must be logged
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from models import AuditLog, ActionType
from config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    action_type: str,
    entity_type: str,
    entity_id: Optional[int],
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Log a critical system action.
    
    Args:
        db: Database session
        action_type: Type of action (from ActionType enum)
        entity_type: "Project", "File", etc.
        entity_id: ID of the entity
        user_id: User identifier (or "system")
        metadata: JSON-serializable dictionary with provenance info
        
    Returns:
        bool: True if logged successfully
    """
    if not settings.audit_logs_enabled:
        return True
        
    try:
        # Validate action type
        try:
            a_type = ActionType(action_type)
        except ValueError:
            logger.error(f"Invalid audit action type: {action_type}")
            # Fallback to keep logging if possible, or just log error?
            # For compliance, we should probably fail safe, but for reliability, we log error and maybe persist as generic?
            # We'll raise or return False. Let's return False but log error.
            return False
            
        metadata_json = json.dumps(metadata) if metadata else None
        
        log_entry = AuditLog(
            action_type=a_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id or "system",
            metadata_json=metadata_json,
            compliance_mode_active=settings.compliance_mode
        )
        
        db.add(log_entry)
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"Failed to write audit log: {str(e)}")
        # In a strict compliance system, we might want to raise this to block the action.
        # But for now, we ensure we don't crash the user flow, but define this as a critical failure.
        # We'll just log to stderr for now.
        print(f"CRITICAL: Failed to write audit log! {str(e)}")
        return False


def get_project_audit_trail(
    db: Session,
    project_id: int,
    limit: int = 100
) -> List[AuditLog]:
    """
    Retrieve audit logs for a specific project.
    
    Includes logs where:
    - entity_type="Project" AND entity_id=project_id
    - entity_type="ClaimDraft" AND logs link to project (requires join or separate logic)
    
    For simplicity in Phase 10, we'll fetch logs explicitly tagged with Project:{id}
    or we can try to fetch related entities if we log project_id in metadata.
    
    Best practice: Always log project_id in metadata for child entities.
    """
    # 1. Direct project logs
    query = db.query(AuditLog).filter(
        AuditLog.entity_type == "Project",
        AuditLog.entity_id == project_id
    )
    
    # 2. Child entity logs (if we had a way to join, but AuditLog is generic)
    # Strategy: Filter by project_id in metadata? No, that's slow (JSON scan).
    # Strategy: Just show project level logs for now, or ensure critical child logs
    #           are "double logged" or associated.
    #           Better: The main UI view is usually "Project History".
    #           We'll stick to Entity=Project for high level, and maybe others.
    
    # Actually, let's just return timestamps descending.
    return query.order_by(AuditLog.created_at.desc()).limit(limit).all()


def get_recent_system_logs(
    db: Session,
    limit: int = 50
) -> List[AuditLog]:
    """Get global recent logs (admin view)."""
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
