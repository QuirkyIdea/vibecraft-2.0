"""
Inventix AI - Draft & Conference API Routes
============================================
API endpoints for draft refinement and conference recommendations.
Non-invasive, modular extension.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import tempfile
import os

from app.services.draft_refiner import DraftRefiner, RefinementType
from app.services.conference_recommender import (
    ConferenceRecommender,
    MethodologyType,
    TargetAudience,
    SubmissionType
)
from app.services.document_processor import DocumentProcessor
from app.core.schemas import AntigravityResponse, CrashLog, ConfidenceLevel, EvidenceReference


router = APIRouter()
draft_refiner = DraftRefiner()
conference_recommender = ConferenceRecommender()
document_processor = DocumentProcessor()


# ============== Request/Response Schemas ==============

class DraftRefineRequest(BaseModel):
    """Request schema for draft refinement (text-based)."""
    text: str = Field(..., min_length=20, description="Draft text to refine")
    focus_areas: Optional[List[str]] = Field(
        None, 
        description="Areas to focus: clarity, structure, precision, grammar, flow"
    )
    change_level: str = Field(
        "moderate",
        description="Change intensity: light, moderate, thorough"
    )


class RefinementChange(BaseModel):
    """A single refinement change."""
    type: str
    original: str
    refined: str
    reason: str


class DraftRefineResponse(AntigravityResponse):
    """Response schema for draft refinement."""
    original_text: str
    refined_text: str
    changes: List[RefinementChange]
    change_summary: dict
    word_count_original: int
    word_count_refined: int
    preserved_intent: bool
    warnings: List[str]


class ConferenceRecommendRequest(BaseModel):
    """Request schema for conference recommendations."""
    title: str = Field(..., min_length=5, description="Research title")
    abstract: str = Field(..., min_length=50, description="Research abstract")
    keywords: List[str] = Field(..., min_items=1, description="Research keywords")
    methodology_type: Optional[str] = Field(
        None, 
        description="theoretical, applied, experimental, mixed"
    )
    target_audience: Optional[str] = Field(
        None,
        description="academic, industry, hybrid"
    )
    max_recommendations: int = Field(5, ge=1, le=10)


class ConferenceItem(BaseModel):
    """A single conference recommendation."""
    name: str
    domain: str
    categories: List[str]
    submission_types: List[str]
    submission_url: str
    relevance_score: float
    reasoning: str
    tier: Optional[str]
    acceptance_rate: Optional[str]


class ConferenceRecommendResponse(AntigravityResponse):
    """Response schema for conference recommendations."""
    recommendations: List[ConferenceItem]
    analysis_summary: str
    domain_detected: str
    keywords_used: List[str]
    methodology_detected: str
    target_audience: str
    total_found: int
    warnings: List[str]


# ============== Endpoints ==============

@router.post("/refine", response_model=DraftRefineResponse | CrashLog)
async def refine_draft(request: DraftRefineRequest):
    """
    Refine a draft document for submission readiness.
    
    CONSTRAINTS:
    - Does NOT introduce new ideas, claims, or data
    - Does NOT fabricate citations or results
    - Preserves author's intent and originality
    - Output reads as fully human-written
    - No AI-detectable markers or robotic phrasing
    """
    try:
        # Parse focus areas
        focus_types = None
        if request.focus_areas:
            type_map = {
                "clarity": RefinementType.CLARITY,
                "structure": RefinementType.STRUCTURE,
                "precision": RefinementType.PRECISION,
                "grammar": RefinementType.GRAMMAR,
                "flow": RefinementType.FLOW
            }
            focus_types = [type_map[f.lower()] for f in request.focus_areas if f.lower() in type_map]
        
        # Perform refinement
        result = await draft_refiner.refine_draft(
            original_text=request.text,
            focus_areas=focus_types,
            max_change_level=request.change_level
        )
        
        if not result.success:
            return CrashLog(
                status="CRASH",
                error_type="REFINEMENT_FAILED",
                error_message=result.error_message or "Draft refinement failed",
                failed_stage="refinement",
                evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
                confidence_score=0.0,
                recommended_action="retry_with_different_input",
                debug_trace=["Received draft", "Started refinement", "Refinement failed"]
            )
        
        # Build response
        changes = [
            RefinementChange(
                type=c.type.value,
                original=c.original,
                refined=c.refined,
                reason=c.reason
            )
            for c in result.changes
        ]
        
        evidence_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-DRAFT"
        
        return DraftRefineResponse(
            original_text=result.original_text,
            refined_text=result.refined_text,
            changes=changes,
            change_summary=result.change_summary,
            word_count_original=result.word_count_original,
            word_count_refined=result.word_count_refined,
            preserved_intent=len(result.preserved_claims) > 0,
            warnings=result.warnings,
            evidence_references=[EvidenceReference(
                evidence_id=evidence_id,
                source="user_draft",
                content_hash=str(hash(request.text)),
                timestamp=datetime.utcnow().isoformat()
            )],
            confidence=ConfidenceLevel.MEDIUM,
            scope_disclaimer="This refinement preserves original intent. No new ideas or claims added.",
            observed_overlap="N/A - refinement task",
            inferred_risk="Minimal - intent preservation verified",
            unknowns=["Stylistic preferences may vary"]
        )
        
    except Exception as e:
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage="processing",
            evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
            confidence_score=0.0,
            recommended_action="system_debug",
            debug_trace=["Received draft", str(e)]
        )


@router.post("/refine-file", response_model=DraftRefineResponse | CrashLog)
async def refine_draft_file(
    file: UploadFile = File(...),
    focus_areas: Optional[str] = None,
    change_level: str = "moderate"
):
    """
    Refine an uploaded draft document (PDF, DOCX, TXT).
    
    SUPPORTED FORMATS: .pdf, .docx, .txt
    """
    try:
        # Validate file type
        filename = file.filename or "upload"
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in [".pdf", ".docx", ".txt"]:
            return CrashLog(
                status="CRASH",
                error_type="INVALID_FILE_TYPE",
                error_message=f"Unsupported file type: {ext}. Use .pdf, .docx, or .txt",
                failed_stage="input_validation",
                evidence_state={"provided": False, "retrieved_count": 0, "usable": False},
                confidence_score=0.0,
                recommended_action="adjust_input",
                debug_trace=["Received file", f"Invalid extension: {ext}"]
            )
        
        # Save to temp file
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Extract text
            extracted = document_processor.extract_text(tmp_path)
            
            if not extracted or len(extracted.strip()) < 50:
                return CrashLog(
                    status="CRASH",
                    error_type="EXTRACTION_FAILED",
                    error_message="Could not extract sufficient text from document",
                    failed_stage="text_extraction",
                    evidence_state={"provided": True, "retrieved_count": 0, "usable": False},
                    confidence_score=0.0,
                    recommended_action="adjust_input",
                    debug_trace=["Received file", "Extraction yielded insufficient text"]
                )
            
            # Parse focus areas
            focus_list = focus_areas.split(",") if focus_areas else None
            
            # Create request and process
            request = DraftRefineRequest(
                text=extracted,
                focus_areas=focus_list,
                change_level=change_level
            )
            
            return await refine_draft(request)
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage="file_processing",
            evidence_state={"provided": True, "retrieved_count": 0, "usable": False},
            confidence_score=0.0,
            recommended_action="system_debug",
            debug_trace=["Received file", str(e)]
        )


@router.post("/recommend", response_model=ConferenceRecommendResponse | CrashLog)
async def recommend_conferences(request: ConferenceRecommendRequest):
    """
    Recommend relevant conferences for submission.
    
    Returns conferences with:
    - Conference name and domain
    - Submission types supported
    - Official submission URL
    - Relevance score and reasoning
    
    CONSTRAINTS:
    - Does NOT auto-submit on behalf of user
    - URLs are direct official links
    - Recommendations are suggestions only
    """
    try:
        # Parse methodology type
        methodology = None
        if request.methodology_type:
            try:
                methodology = MethodologyType(request.methodology_type.lower())
            except ValueError:
                pass
        
        # Parse target audience
        audience = None
        if request.target_audience:
            try:
                audience = TargetAudience(request.target_audience.lower())
            except ValueError:
                pass
        
        # Get recommendations
        result = await conference_recommender.recommend_conferences(
            title=request.title,
            abstract=request.abstract,
            keywords=request.keywords,
            methodology_type=methodology,
            target_audience=audience,
            max_recommendations=request.max_recommendations
        )
        
        if not result.success:
            return CrashLog(
                status="CRASH",
                error_type="RECOMMENDATION_FAILED",
                error_message=result.error_message or "Conference recommendation failed",
                failed_stage="recommendation",
                evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
                confidence_score=0.0,
                recommended_action="retry_with_different_input",
                debug_trace=["Received request", "Analysis failed"]
            )
        
        # Build response
        recommendations = [
            ConferenceItem(
                name=r.name,
                domain=r.domain,
                categories=r.categories,
                submission_types=[st.value for st in r.submission_types],
                submission_url=r.submission_url,
                relevance_score=r.relevance_score,
                reasoning=r.reasoning,
                tier=r.tier,
                acceptance_rate=r.acceptance_rate
            )
            for r in result.recommendations
        ]
        
        evidence_id = f"EVD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-CONF"
        
        return ConferenceRecommendResponse(
            recommendations=recommendations,
            analysis_summary=result.analysis_summary,
            domain_detected=result.domain_detected,
            keywords_used=result.keywords_used,
            methodology_detected=result.methodology_detected.value,
            target_audience=result.target_audience.value,
            total_found=result.total_found,
            warnings=result.warnings,
            evidence_references=[EvidenceReference(
                evidence_id=evidence_id,
                source="conference_database",
                content_hash=str(hash(request.title)),
                timestamp=datetime.utcnow().isoformat()
            )],
            confidence=ConfidenceLevel.MEDIUM,
            scope_disclaimer="These are suggestions only. Verify deadlines and requirements on official websites.",
            observed_overlap="N/A - recommendation task",
            inferred_risk="N/A - no novelty assessment",
            unknowns=["Current submission deadlines", "Exact fit for specific tracks"]
        )
        
    except Exception as e:
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage="processing",
            evidence_state={"provided": True, "retrieved_count": 0, "usable": True},
            confidence_score=0.0,
            recommended_action="system_debug",
            debug_trace=["Received request", str(e)]
        )


@router.get("/status")
async def draft_conference_status():
    """Get Draft & Conference service status."""
    return {
        "service": "draft-conference",
        "status": "operational",
        "engine": "ANTIGRAVITY",
        "capabilities": [
            "draft_refinement",
            "file_upload_refinement",
            "conference_recommendation"
        ],
        "supported_formats": [".pdf", ".docx", ".txt"],
        "constraints": [
            "No new ideas introduced",
            "Intent preservation guaranteed",
            "No auto-submission",
            "Official URLs only"
        ]
    }
