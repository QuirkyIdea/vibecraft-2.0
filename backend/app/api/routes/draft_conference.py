"""
Inventix AI - Draft & Conference API Routes
============================================
API endpoints for draft refinement and conference recommendations.
Non-invasive, modular extension.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import tempfile
import os
import logging
import difflib
import json

logger = logging.getLogger(__name__)

from app.services.draft_refiner import DraftRefiner, RefinementType
from app.services.conference_recommender import (
    ConferenceRecommender,
    MethodologyType,
    TargetAudience,
    SubmissionType
)
from app.services.document_processor import DocumentProcessor
from app.core.schemas import (
    AntigravityResponse, CrashLog, ConfidenceLevel, EvidenceReference,
    FailedStage, RecommendedAction, EvidenceState
)


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
    accepted: bool = Field(True, description="Whether this change is accepted")
    id: Optional[str] = Field(None, description="Unique ID for this change")


class SectionRefineRequest(BaseModel):
    """Request schema for section-specific refinement."""
    section_text: str = Field(..., min_length=20, description="Section text to refine")
    section_type: str = Field(..., description="abstract, introduction, methodology, results, discussion, conclusion")
    target_improvements: Optional[List[str]] = Field(None, description="Specific improvements to target")


class BatchRefineRequest(BaseModel):
    """Request schema for batch file refinement."""
    focus_areas: Optional[List[str]] = None
    change_level: str = "moderate"


class ExportRequest(BaseModel):
    """Request schema for exporting refined text."""
    original_text: str = Field(default="", description="Original draft text")
    refined_text: str = Field(..., description="Refined draft text")


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
    diff_html: Optional[str] = Field(None, description="HTML diff for comparison view")


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
        logger.error(f"REFINE CALLED: text_len={len(request.text)}, focus={request.focus_areas}, change_level={request.change_level}")
        
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
        
        logger.error(f"REFINE: Parsed focus_types={focus_types}")
        
        # Perform refinement
        result = await draft_refiner.refine_draft(
            original_text=request.text,
            focus_areas=focus_types,
            max_change_level=request.change_level
        )
        
        logger.error(f"REFINE: draft_refiner returned success={result.success}")
        
        if not result.success:
            logger.error(f"REFINE FAILED: {result.error_message}")
            return CrashLog(
                status="CRASH",
                error_type="REFINEMENT_FAILED",
                error_message=result.error_message or "Draft refinement failed",
                failed_stage=FailedStage.REFINEMENT,
                evidence_state=EvidenceState(provided=True, retrieved_count=0, usable=True),
                confidence_score=0.0,
                recommended_action=RecommendedAction.RETRY_WITH_DIFFERENT_INPUT,
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
        
        # Generate HTML diff for comparison view
        diff_html = _generate_html_diff(result.original_text, result.refined_text)
        
        # Add unique IDs to changes
        for idx, change in enumerate(changes):
            change.id = f"change-{idx}"
        
        logger.error("REFINE SUCCESS")
        
        return DraftRefineResponse(
            original_text=result.original_text,
            refined_text=result.refined_text,
            changes=changes,
            change_summary=result.change_summary,
            word_count_original=result.word_count_original,
            word_count_refined=result.word_count_refined,
            preserved_intent=len(result.preserved_claims) > 0,
            warnings=result.warnings,
            diff_html=diff_html,
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
        logger.error(f"REFINE EXCEPTION: {type(e).__name__}: {str(e)}", exc_info=True)
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage=FailedStage.PROCESSING,
            evidence_state=EvidenceState(provided=True, retrieved_count=0, usable=True),
            confidence_score=0.0,
            recommended_action=RecommendedAction.SYSTEM_DEBUG,
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
    temp_path = None
    try:
        logger.error(f"REFINE-FILE CALLED: filename={file.filename}, focus_areas={focus_areas}, change_level={change_level}")
        
        # Validate file type
        filename = file.filename or "upload"
        ext = os.path.splitext(filename)[1].lower()
        
        logger.error(f"REFINE-FILE: File extension={ext}")
        
        if ext not in [".pdf", ".docx", ".txt"]:
            logger.error(f"REFINE-FILE FAILED: Invalid file type {ext}")
            return CrashLog(
                status="CRASH",
                error_type="INVALID_FILE_TYPE",
                error_message=f"Unsupported file type: {ext}. Use .pdf, .docx, or .txt",
                failed_stage=FailedStage.INPUT_VALIDATION,
                evidence_state=EvidenceState(provided=False, retrieved_count=0, usable=False),
                confidence_score=0.0,
                recommended_action=RecommendedAction.ADJUST_INPUT,
                debug_trace=["Received file", f"Invalid extension: {ext}"]
            )
        
        # Save to temp file
        content = await file.read()
        logger.error(f"REFINE-FILE: Read {len(content)} bytes from file")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            temp_path = tmp.name
        
        logger.error(f"REFINE-FILE: Saved to temp file: {temp_path}")
        
        try:
            # Extract text
            logger.error(f"REFINE-FILE: Calling document_processor.extract_text({temp_path})")
            extracted = document_processor.extract_text(temp_path)
            logger.error(f"REFINE-FILE: Extracted {len(extracted)} characters")
            
            if not extracted or len(extracted.strip()) < 50:
                logger.error(f"REFINE-FILE FAILED: Insufficient text extracted (len={len(extracted) if extracted else 0})")
                return CrashLog(
                    status="CRASH",
                    error_type="EXTRACTION_FAILED",
                    error_message="Could not extract sufficient text from document",
                    failed_stage=FailedStage.TEXT_EXTRACTION,
                    evidence_state=EvidenceState(provided=True, retrieved_count=0, usable=False),
                    confidence_score=0.0,
                    recommended_action=RecommendedAction.ADJUST_INPUT,
                    debug_trace=["Received file", "Extraction yielded insufficient text"]
                )
            
            # Parse focus areas
            focus_list = focus_areas.split(",") if focus_areas else None
            logger.error(f"REFINE-FILE: Parsed focus_list={focus_list}")
            
            # Create request and process
            request = DraftRefineRequest(
                text=extracted,
                focus_areas=focus_list,
                change_level=change_level
            )
            
            logger.error("REFINE-FILE: Calling refine_draft()")
            result = await refine_draft(request)
            logger.error("REFINE-FILE SUCCESS")
            return result
            
        finally:
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.error(f"REFINE-FILE: Cleaned up temp file {temp_path}")
            
    except Exception as e:
        logger.error(f"REFINE-FILE EXCEPTION: {type(e).__name__}: {str(e)}", exc_info=True)
        return CrashLog(
            status="CRASH",
            error_type="UNKNOWN_FAILURE",
            error_message=str(e),
            failed_stage=FailedStage.FILE_PROCESSING,
            evidence_state=EvidenceState(provided=True, retrieved_count=0, usable=False),
            confidence_score=0.0,
            recommended_action=RecommendedAction.SYSTEM_DEBUG,
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
                failed_stage=FailedStage.RECOMMENDATION,
                evidence_state=EvidenceState(provided=True, retrieved_count=0, usable=True),
                confidence_score=0.0,
                recommended_action=RecommendedAction.RETRY_WITH_DIFFERENT_INPUT,
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
            failed_stage=FailedStage.PROCESSING,
            evidence_state=EvidenceState(provided=True, retrieved_count=0, usable=True),
            confidence_score=0.0,
            recommended_action=RecommendedAction.SYSTEM_DEBUG,
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
            "conference_recommendation",
            "section_refinement",
            "batch_processing",
            "export_formats"
        ],
        "supported_formats": [".pdf", ".docx", ".txt"],
        "export_formats": ["txt", "docx", "pdf"],
        "constraints": [
            "No new ideas introduced",
            "Intent preservation guaranteed",
            "No auto-submission",
            "Official URLs only"
        ]
    }


# ============== Helper Functions ==============

def _generate_html_diff(original: str, refined: str) -> str:
    """Generate HTML diff for side-by-side comparison."""
    diff = difflib.HtmlDiff(wrapcolumn=80)
    html = diff.make_table(
        original.splitlines(),
        refined.splitlines(),
        fromdesc="Original",
        todesc="Refined",
        context=True,
        numlines=3
    )
    return html


# ============== New Endpoints ==============

@router.post("/refine-section", response_model=dict)
async def refine_section(request: SectionRefineRequest):
    """
    Refine a specific section of a document.
    
    Supports: abstract, introduction, methodology, results, discussion, conclusion
    """
    try:
        result = await draft_refiner.refine_section(
            section_text=request.section_text,
            section_type=request.section_type,
            target_improvements=request.target_improvements
        )
        
        if result.get("success"):
            return {
                "success": True,
                "refined": result.get("refined", ""),
                "improvements_made": result.get("improvements_made", []),
                "preserved_elements": result.get("preserved_elements", []),
                "suggestions": result.get("suggestions", [])
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Section refinement failed"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refine-batch", response_model=List[dict])
async def refine_batch(
    files: List[UploadFile] = File(...),
    focus_areas: Optional[str] = None,
    change_level: str = "moderate"
):
    """
    Refine multiple files in batch.
    
    Returns a list of results, one per file.
    """
    results = []
    
    for file in files:
        temp_path = None
        try:
            # Save file temporarily
            filename = file.filename or "upload"
            ext = os.path.splitext(filename)[1].lower()
            
            if ext not in [".pdf", ".docx", ".txt"]:
                results.append({
                    "filename": filename,
                    "success": False,
                    "error": f"Unsupported file type: {ext}"
                })
                continue
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                content = await file.read()
                tmp.write(content)
                temp_path = tmp.name
            
            # Extract text
            extracted = document_processor.extract_text(temp_path)
            
            # Parse focus areas
            focus_list = focus_areas.split(",") if focus_areas else ["clarity", "grammar"]
            type_map = {
                "clarity": RefinementType.CLARITY,
                "structure": RefinementType.STRUCTURE,
                "precision": RefinementType.PRECISION,
                "grammar": RefinementType.GRAMMAR,
                "flow": RefinementType.FLOW
            }
            focus_types = [type_map[f.strip().lower()] for f in focus_list if f.strip().lower() in type_map]
            
            # Refine
            result = await draft_refiner.refine_draft(
                original_text=extracted,
                focus_areas=focus_types,
                max_change_level=change_level
            )
            
            if result.success:
                results.append({
                    "filename": filename,
                    "success": True,
                    "original_text": result.original_text[:500] + "..." if len(result.original_text) > 500 else result.original_text,
                    "refined_text": result.refined_text[:500] + "..." if len(result.refined_text) > 500 else result.refined_text,
                    "changes_count": len(result.changes),
                    "word_count_original": result.word_count_original,
                    "word_count_refined": result.word_count_refined
                })
            else:
                results.append({
                    "filename": filename,
                    "success": False,
                    "error": result.error_message
                })
        
        except Exception as e:
            results.append({
                "filename": file.filename or "unknown",
                "success": False,
                "error": str(e)
            })
        
        finally:
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
    
    return results


@router.post("/export/{format}")
async def export_refined_text(
    format: str,
    request: ExportRequest
):
    """
    Export refined text in various formats.
    
    Supported formats: txt, docx, pdf
    """
    if format not in ["txt", "docx", "pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported format. Use: txt, docx, pdf")
    
    if not request.refined_text:
        raise HTTPException(status_code=400, detail="refined_text is required")
    
    try:
        if format == "txt":
            content = f"ORIGINAL TEXT:\n\n{request.original_text}\n\n{'='*80}\n\nREFINED TEXT:\n\n{request.refined_text}"
            return Response(
                content=content,
                media_type="text/plain",
                headers={"Content-Disposition": "attachment; filename=refined_draft.txt"}
            )
        
        elif format == "docx":
            from docx import Document
            doc = Document()
            doc.add_heading("Draft Refinement Results", 0)
            doc.add_heading("Original Text", level=1)
            doc.add_paragraph(request.original_text)
            doc.add_heading("Refined Text", level=1)
            doc.add_paragraph(request.refined_text)
            
            # Save to bytes
            import io
            file_stream = io.BytesIO()
            doc.save(file_stream)
            file_stream.seek(0)
            
            return Response(
                content=file_stream.getvalue(),
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": "attachment; filename=refined_draft.docx"}
            )
        
        elif format == "pdf":
            # Simple PDF generation using reportlab
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                import io
                
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                story.append(Paragraph("Draft Refinement Results", styles['Title']))
                story.append(Spacer(1, 12))
                story.append(Paragraph("Original Text", styles['Heading1']))
                story.append(Paragraph(request.original_text.replace('\n', '<br/>'), styles['BodyText']))
                story.append(Spacer(1, 12))
                story.append(Paragraph("Refined Text", styles['Heading1']))
                story.append(Paragraph(request.refined_text.replace('\n', '<br/>'), styles['BodyText']))
                
                doc.build(story)
                buffer.seek(0)
                
                return Response(
                    content=buffer.getvalue(),
                    media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=refined_draft.pdf"}
                )
            except ImportError:
                raise HTTPException(
                    status_code=500, 
                    detail="PDF export not available. Install reportlab: pip install reportlab"
                )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
