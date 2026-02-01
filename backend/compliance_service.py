"""
Compliance Service for Inventix AI - Phase 10

Enforces operational modes and restricts risky features.
System-wide "Safety Switch".

HARD RULES:
- Compliance Mode = TRUE -> strict restrictions applied
- No bypass allowed via API
"""
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

from config import get_settings

settings = get_settings()


class ComplianceViolation(Exception):
    """Raised when an action is blocked by compliance rules."""
    pass


# Feature Flags and Restrictions
RESTRICTED_FEATURES = {
    "PATENT_CLAIM_GENERATION": {
        "allowed_in_compliance": False,
        "reason": "Patent claim generation is disabled in Compliance Mode to prevent unauthorized legal practice."
    },
    "DRAFT_OPTIMIZATION_CREATIVE": {
        "allowed_in_compliance": False,
        "reason": "Creative rewriting is disabled. Only clarity/grammar fixes allowed."
    },
    "HIGH_RISK_NOVELTY_CHECK": {
        "allowed_in_compliance": True,
        "reason": "Novelty checking is allowed but creates permanent audit records."
    }
}


def is_compliance_mode_active() -> bool:
    """Check if system is in compliance mode."""
    return settings.compliance_mode


def validate_feature_access(feature_name: str):
    """
    Validate if a feature can be accessed.
    
    Raises:
        HTTPException(403) if blocked.
    """
    if not is_compliance_mode_active():
        return  # Normal mode: everything allowed
        
    rule = RESTRICTED_FEATURES.get(feature_name)
    if rule and not rule["allowed_in_compliance"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Compliance Restriction: {rule['reason']}"
        )


def check_draft_optimization_params(instruction: str) -> str:
    """
    Sanitize or validate draft optimization instructions in compliance mode.
    
    If in Compliance Mode, force instruction to be "Improve clarity and grammar only".
    """
    if is_compliance_mode_active():
        # Override user instruction
        return "Improve clarity, grammar, and academic tone. Do not add new ideas or change the meaning."
    return instruction


def get_system_compliance_status() -> Dict[str, Any]:
    """Get current compliance status for UI."""
    return {
        "compliance_mode_active": is_compliance_mode_active(),
        "restricted_features": [
            k for k, v in RESTRICTED_FEATURES.items() if not v["allowed_in_compliance"]
        ],
        "audit_logging_enabled": settings.audit_logs_enabled
    }
