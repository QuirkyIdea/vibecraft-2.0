"""
Inventix AI Backend - Phase 8
FastAPI Application Entry Point

This backend provides:
- Project CRUD operations
- File upload and storage
- Truthful analysis state tracking
- AI ASSISTANCE (not decisions!)
- Text extraction from documents
- Evidence retrieval from external sources
- DETERMINISTIC SIMILARITY SCORING
- NOVELTY RISK CLASSIFICATION
- DRAFT OPTIMIZATION (localized suggestions)
- VENUE RECOMMENDATIONS (suggestions only)
- PATENT CLAIM STRUCTURING (conceptual only)

Phase 8 Features:
- Patent claim hierarchy generation
- Dependency graph visualization
- Risk annotations linked to evidence
- Attorney handoff notes
- LEGAL DISCLAIMERS ALWAYS PRESENT

HARD RULES:
- Similarity from REAL text only
- Every score links to specific evidence
- No LLM-only similarity judgments
- Same input → same score (deterministic)
- Venue recommendations are SUGGESTIONS only
- Patent claims are CONCEPTUAL DRAFTS only
- NO patentability assertions
- NO legal advice
"""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List
import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File as FastAPIFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from config import get_settings, ensure_upload_dir
from database import get_db, init_db, SessionLocal
from schemas import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse, 
    ProjectDetailResponse,
    ProjectListResponse,
    FileResponse as FileSchema,
    SuccessResponse,
    ErrorResponse,
    AIAssistanceRequest,
    AIAssistanceResponse,
    # Phase 3 schemas
    TextExtractionResult,
    KeywordExtractionRequest,
    KeywordExtractionResponse,
    RetrievalRequest,
    RetrievalResponse,
    ProjectEvidenceResponse,
    EvidenceCandidateResponse,
    # Phase 4 schemas
    NoveltyRiskLevel,
    EmbeddingGenerationResponse,
    SimilarityComputationResponse,
    NoveltyRiskResponse,
    SimilarityMatch,
    SimilarityListResponse,
    # Phase 5 schemas
    ComparativeAnalysisRequest,
    ComparativeAnalysisResponse,
    ComparativeAnalysisSummary,
    OverlapPoint,
    DifferencePoint,
    EvidenceSummaryItem,
    # Phase 6 schemas
    DraftOptimizeRequest,
    DraftOptimizeResponse,
    DraftSuggestionItem,
    SuggestionUpdateRequest,
    SuggestionUpdateResponse,
    DraftVersionResponse,
    DraftHistoryResponse,
    SuggestionStatus,
    ChangeType,
    PreservesIntent,
    # Phase 7 schemas
    VenueRecommendationRequest,
    VenueRecommendationResponse,
    VenueRecommendationItem,
    ReadinessNotesResponse,
    ReadinessLevel,
    VenueType as VenueTypeSchema,
    # Phase 8 schemas
    ClaimType as ClaimTypeSchema,
    ClaimRiskType as ClaimRiskTypeSchema,
    ClaimFlagType as ClaimFlagTypeSchema,
    ClaimDraftItem,
    ClaimRiskAnnotationItem,
    ClaimDependencyEdge,
    ClaimDependencyGraph,
    AttorneyHandoffNotes,
    ClaimGenerationRequest,
    ClaimGenerationResponse,
    ClaimUpdateRequest,
    ClaimUpdateResponse,
    ClaimFlagRequest,
    ClaimFlagResponse,
    ClaimsListResponse,
    FeedbackRequest,
    FeedbackResponse,
    FeedbackSummaryResponse,
    ProjectFeedbackStatsResponse,
    ConfidenceCalibrationResponse,
    FeedbackItem,
    ConfidenceLevelResponse,
    AuditLogListResponse,
    ComplianceStatusResponse,
    AuditLogItem
)
from models import (
    AnalysisStatus, AIAction, ExtractedText, CandidateEvidence, EvidenceSource,
    NoveltyRiskLevel as NoveltyRiskLevelModel, IdeaEmbedding, EvidenceEmbedding, SimilarityScore,
    ComparativeAnalysis, DraftVersion, DraftSuggestion,
    SuggestionStatus as SuggestionStatusModel, ChangeType as ChangeTypeModel, PreservesIntent as PreservesIntentModel,
    ClaimDraft, ClaimRiskAnnotation, ClaimGenerationMetadata,
    ClaimType as ClaimTypeModel, ClaimRiskType as ClaimRiskTypeModel, ClaimFlagType as ClaimFlagTypeModel,
    ProjectType,
    UserFeedback, ConfidenceCalibration, FeedbackType, OutputType, ConfidenceLevel,
    AuditLog, ActionType
)
import crud
import ai_service
import text_extraction
import retrieval_service
import embedding_service
import similarity_engine
import comparative_service
import draft_service
import recommendation_service
import claim_service
import feedback_service
import calibration_service
import audit_service
import compliance_service


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown"""
    # Startup
    print("=" * 50)
    print("Starting Inventix AI Backend - Phase 10")
    print("=" * 50)
    init_db()
    ensure_upload_dir()
    
    # System Integrity Checks
    print("Running system integrity checks...")
    integrity_ok = True
    
    # 1. DB Connection
    try:
        from crud import get_project_count
        db_check = SessionLocal()
        get_project_count(db_check)
        db_check.close()
        print(" [x] Database connection: OK")
    except Exception as e:
        print(f" [!] Database connection: FAILED ({str(e)})")
        integrity_ok = False
        
    # 2. Upload Dir
    if os.path.exists(settings.upload_dir):
        print(" [x] Upload directory: OK")
    else:
         print(" [!] Upload directory: MISSING")
         integrity_ok = False
         
    # 3. Mode Check
    if settings.compliance_mode:
        print(" [!] COMPLIANCE MODE: ACTIVE (Restricted features enabled)")
    else:
        print(" [i] Compliance Mode: OFF (Normal operation)")
        
    if not integrity_ok:
        print("CRITICAL: System integrity checks failed! Startup may be unstable.")
    else:
        print("System integrity checks passed.")

    print(f"Upload directory: {settings.upload_dir}")
    print(f"Database: {settings.database_url}")
    print(f"CORS origins: {settings.cors_origins_list}")
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"LLM Model: {settings.llm_model}")
    print(f"Embedding Model: {settings.embedding_model}")
    
    # Check if LLM is configured
    if not settings.llm_api_key or settings.llm_api_key == "your-nebius-api-key-here":
        print("WARNING: LLM API key not configured!")
    else:
        print("LLM API key: configured")
    
    print("Text Extraction: PDF, DOCX, TXT")
    print("External Retrieval: Semantic Scholar, USPTO")
    print("Similarity Scoring: Cosine similarity on embeddings")
    print("Novelty Risk: GREEN/YELLOW/RED/UNKNOWN")
    print("Patent Claims: Conceptual structuring (NOT legal advice)")
    print("Trust Control: Human Feedback & Confidence Calibration")
    print("Audit Logging: " + ("ENABLED" if settings.audit_logs_enabled else "DISABLED"))
    print("=" * 50)
    
    # Audit Startup
    db = SessionLocal()
    audit_service.log_action(db, "SYSTEM_STARTUP", "System", None, metadata={"version": "1.0.0"})
    db.close()
    
    yield
    # Shutdown
    print("Shutting down Inventix AI Backend")


app = FastAPI(
    title="Inventix AI Backend",
    description="""
    Phase 10 Backend - Audit Logs & Compliance
    
    This backend provides:
    - Honest, persistent data storage
    - AI assistance for idea clarification, text rewriting, and risk awareness
    - REAL text extraction from PDF/DOCX files
    - REAL evidence retrieval from Semantic Scholar and USPTO
    - DETERMINISTIC similarity scoring (cosine similarity on embeddings)
    - NOVELTY RISK classification (GREEN/YELLOW/RED/UNKNOWN)
    - DRAFT OPTIMIZATION with localized suggestions
    - VENUE RECOMMENDATIONS based on topic and novelty
    - PATENT CLAIM STRUCTURING (conceptual only)
    - TRUST CONTROL via human feedback and confidence calibration
    - AUDIT LOGS & COMPLIANCE ENFORCEMENT for institutional use
    
    HARD RULES:
    - Similarity from REAL text only
    - Same input = same score (deterministic)
    - Patent claims are CONCEPTUAL DRAFTS only
    - NO patentability assertions
    - NO legal advice
    - AI outputs NEVER self-validate
    - Human feedback preserved (never overwritten)
    - COMPLIANCE MODE restricts risky features
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    llm_configured = bool(settings.llm_api_key and settings.llm_api_key != "your-nebius-api-key-here")
    return {
        "status": "healthy",
        "phase": 10,
        "ai_enabled": llm_configured,
        "ai_provider": settings.llm_provider if llm_configured else None,
        "text_extraction": True,
        "evidence_retrieval": True,
        "venue_recommendations": True,
        "patent_claims": True,
        "audit_logs": True,
        "compliance_mode": settings.compliance_mode,
        "message": "Phase 10 backend operational. Functionally complete."
    }


# ============== Project Endpoints ==============

@app.post(
    f"{settings.api_prefix}/projects", 
    response_model=ProjectDetailResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Projects"]
)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project.
    
    The project will be persisted in the database.
    An analysis state is automatically created with status=NOT_STARTED.
    """
    db_project = crud.create_project(db=db, project=project)
    
    # Phase 10: Audit Log
    audit_service.log_action(
        db, 
        "PROJECT_CREATED", 
        "Project", 
        db_project.id, 
        None, 
        metadata={"title": db_project.title, "type": db_project.type}
    )
    
    return db_project


@app.get(
    f"{settings.api_prefix}/projects",
    response_model=ProjectListResponse,
    tags=["Projects"]
)
def list_projects(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List all projects.
    
    Returns projects ordered by creation date (newest first).
    """
    projects = crud.get_projects(db, skip=skip, limit=limit)
    total = crud.get_projects_count(db)
    return ProjectListResponse(projects=projects, total=total)


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}",
    response_model=ProjectDetailResponse,
    tags=["Projects"]
)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get a project by ID.
    
    Includes files list and analysis state.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return db_project


@app.put(
    f"{settings.api_prefix}/projects/{{project_id}}",
    response_model=ProjectDetailResponse,
    tags=["Projects"]
)
def update_project(
    project_id: int, 
    project: ProjectUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update a project.
    
    Only provided fields will be updated.
    Analysis state is automatically recalculated.
    """
    db_project = crud.update_project(db, project_id, project)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return db_project


@app.delete(
    f"{settings.api_prefix}/projects/{{project_id}}",
    response_model=SuccessResponse,
    tags=["Projects"]
)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project and all associated files.
    
    This action cannot be undone.
    """
    success = crud.delete_project(db, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return SuccessResponse(message=f"Project {project_id} deleted successfully")


# ============== File Endpoints ==============

@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/files",
    response_model=FileSchema,
    status_code=status.HTTP_201_CREATED,
    tags=["Files"]
)
async def upload_file(
    project_id: int,
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file to a project.
    
    Accepted formats: PDF, DOCX, DOC, TXT
    Max size: 50MB
    """
    # Check project exists
    if not crud.get_project(db, project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Check file size
    if file.size and file.size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
        )
    
    # Save file
    db_file = crud.save_uploaded_file(db, project_id, file)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {settings.allowed_extensions}"
        )
    
    return db_file


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/files",
    response_model=List[FileSchema],
    tags=["Files"]
)
def list_project_files(project_id: int, db: Session = Depends(get_db)):
    """
    List all files for a project.
    """
    if not crud.get_project(db, project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return crud.get_project_files(db, project_id)


@app.delete(
    f"{settings.api_prefix}/projects/{{project_id}}/files/{{file_id}}",
    response_model=SuccessResponse,
    tags=["Files"]
)
def delete_file(project_id: int, file_id: int, db: Session = Depends(get_db)):
    """
    Delete a file from a project.
    
    Removes from both disk and database.
    """
    db_file = crud.get_file(db, file_id)
    if not db_file or db_file.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found in project {project_id}"
        )
    
    crud.delete_file(db, file_id)
    return SuccessResponse(message=f"File {file_id} deleted successfully")


@app.get(
    f"{settings.api_prefix}/files/{{file_id}}/download",
    tags=["Files"]
)
def download_file(file_id: int, db: Session = Depends(get_db)):
    """
    Download a file by ID.
    """
    db_file = crud.get_file(db, file_id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} not found"
        )
    
    if not os.path.exists(db_file.storage_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File no longer exists on disk"
        )
    
    return FileResponse(
        path=db_file.storage_path,
        filename=db_file.original_filename,
        media_type="application/octet-stream"
    )


# ============== Phase 3: Text Extraction Endpoints ==============

@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/extract-text",
    response_model=TextExtractionResult,
    tags=["Text Extraction"]
)
def extract_text_from_project(project_id: int, db: Session = Depends(get_db)):
    """
    Extract real text from all uploaded files in a project.
    
    Supports: PDF, DOCX, TXT
    
    ⚠️ Note: This extracts ACTUAL text only.
    - Scanned PDFs may yield no text
    - Results are stored in database
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    files = crud.get_project_files(db, project_id)
    if not files:
        return TextExtractionResult(
            success=False,
            project_id=project_id,
            files_processed=0,
            total_characters=0,
            extraction_notes="No files uploaded to extract text from.",
            errors=["No files found"]
        )
    
    total_chars = 0
    processed = 0
    errors = []
    
    for file in files:
        # Check if already extracted
        existing = db.query(ExtractedText).filter(ExtractedText.file_id == file.id).first()
        
        result = text_extraction.extract_text(file.storage_path, file.file_type)
        
        if result.success:
            if existing:
                # Update existing
                existing.content = result.content
                existing.character_count = result.character_count
                existing.extraction_method = result.method
                existing.extracted_at = datetime.utcnow()
                existing.version += 1
            else:
                # Create new
                extracted = ExtractedText(
                    project_id=project_id,
                    file_id=file.id,
                    content=result.content,
                    extraction_method=result.method,
                    character_count=result.character_count
                )
                db.add(extracted)
            
            total_chars += result.character_count
            processed += 1
        else:
            errors.append(f"{file.original_filename}: {result.error}")
    
    # Update analysis state
    if db_project.analysis_state:
        db_project.analysis_state.text_extracted = processed > 0
        db_project.analysis_state.notes = f"Text extracted from {processed} file(s)."
    
    db.commit()
    
    return TextExtractionResult(
        success=processed > 0,
        project_id=project_id,
        files_processed=processed,
        total_characters=total_chars,
        extraction_notes=f"Extracted text from {processed}/{len(files)} files. Total {total_chars} characters.",
        errors=errors
    )


# ============== Phase 3: Keyword Extraction Endpoints ==============

@app.post(
    f"{settings.api_prefix}/analysis/extract-keywords",
    response_model=KeywordExtractionResponse,
    tags=["Keyword Extraction"]
)
def extract_keywords(request: KeywordExtractionRequest, db: Session = Depends(get_db)):
    """
    Extract keywords, concepts, and technical phrases using LLM.
    
    ⚠️ AI ASSISTANCE ONLY
    - Keywords are suggestions, not facts
    - Human review is required
    """
    db_project = crud.get_project(db, request.project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {request.project_id} not found"
        )
    
    # Get text: from request, extracted texts, or idea_text
    text_to_analyze = request.text
    
    if not text_to_analyze:
        # Try extracted texts
        extracted = db.query(ExtractedText).filter(
            ExtractedText.project_id == request.project_id
        ).all()
        
        if extracted:
            text_to_analyze = " ".join([e.content[:2000] for e in extracted])
        elif db_project.idea_text:
            text_to_analyze = db_project.idea_text
        else:
            return KeywordExtractionResponse(
                success=False,
                keywords=[],
                concepts=[],
                technical_phrases=[],
                error="No text available. Upload files and extract text first, or provide text directly."
            )
    
    # Truncate for LLM
    text_to_analyze = text_to_analyze[:5000]
    
    # Use LLM for extraction
    prompt = retrieval_service.create_keyword_extraction_prompt(text_to_analyze)
    
    try:
        result = ai_service.call_llm(prompt, max_tokens=500)
        
        if result.success:
            # Parse JSON response
            try:
                parsed = json.loads(result.ai_output)
                return KeywordExtractionResponse(
                    success=True,
                    keywords=parsed.get("keywords", []),
                    concepts=parsed.get("concepts", []),
                    technical_phrases=parsed.get("technical_phrases", [])
                )
            except json.JSONDecodeError:
                # Fallback: extract words from response
                words = [w.strip() for w in result.ai_output.split(",") if w.strip()]
                return KeywordExtractionResponse(
                    success=True,
                    keywords=words[:10],
                    concepts=[],
                    technical_phrases=[],
                    notes="Keywords extracted (JSON parsing failed, used fallback)."
                )
        else:
            return KeywordExtractionResponse(
                success=False,
                keywords=[],
                concepts=[],
                technical_phrases=[],
                error=result.error
            )
            
    except Exception as e:
        return KeywordExtractionResponse(
            success=False,
            keywords=[],
            concepts=[],
            technical_phrases=[],
            error=f"Keyword extraction failed: {str(e)}"
        )


# ============== Phase 3: Evidence Retrieval Endpoints ==============

@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/retrieve-papers",
    response_model=RetrievalResponse,
    tags=["Evidence Retrieval"]
)
async def retrieve_research_papers(
    project_id: int,
    request: RetrievalRequest,
    db: Session = Depends(get_db)
):
    """
    Retrieve research papers from Semantic Scholar.
    
    ⚠️ CANDIDATE EVIDENCE ONLY
    - These are NOT "similar" to your idea
    - No similarity scores computed
    - No novelty claims made
    - Every result has a verifiable URL
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get keywords
    keywords = request.keywords
    if not keywords:
        # Use idea text as fallback
        if db_project.idea_text:
            keywords = db_project.idea_text.split()[:10]
        else:
            return RetrievalResponse(
                success=False,
                source="Semantic Scholar",
                candidates_stored=0,
                search_query="",
                retrieval_notes="",
                error="No keywords provided and no idea text available."
            )
    
    # Call Semantic Scholar
    result = await retrieval_service.search_research_papers(keywords, limit=request.limit)
    
    if not result.success:
        return RetrievalResponse(
            success=False,
            source="Semantic Scholar",
            candidates_stored=0,
            search_query=result.search_query,
            retrieval_notes="",
            error=result.error
        )
    
    # Store candidates
    stored = 0
    for candidate in result.candidates:
        evidence = CandidateEvidence(
            project_id=project_id,
            source_type="paper",
            title=candidate.title,
            authors=candidate.authors,
            abstract=candidate.abstract,
            source_name=EvidenceSource.SEMANTIC_SCHOLAR,
            source_url=candidate.source_url,
            publication_date=candidate.publication_date,
            search_query=result.search_query
        )
        db.add(evidence)
        stored += 1
    
    # Update analysis state
    if db_project.analysis_state:
        db_project.analysis_state.evidence_retrieved = True
        db_project.analysis_state.retrieval_notes = f"Retrieved {stored} research papers. No similarity scores computed."
    
    db.commit()
    
    return RetrievalResponse(
        success=True,
        source="Semantic Scholar",
        candidates_stored=stored,
        search_query=result.search_query,
        retrieval_notes=result.retrieval_notes
    )


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/retrieve-patents",
    response_model=RetrievalResponse,
    tags=["Evidence Retrieval"]
)
async def retrieve_patents(
    project_id: int,
    request: RetrievalRequest,
    db: Session = Depends(get_db)
):
    """
    Retrieve patents from USPTO.
    
    ⚠️ CANDIDATE EVIDENCE ONLY
    - These are NOT "similar" to your idea
    - No similarity scores computed
    - No novelty claims made
    - Every result has a verifiable URL
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get keywords
    keywords = request.keywords
    if not keywords:
        if db_project.idea_text:
            keywords = db_project.idea_text.split()[:10]
        else:
            return RetrievalResponse(
                success=False,
                source="USPTO",
                candidates_stored=0,
                search_query="",
                retrieval_notes="",
                error="No keywords provided and no idea text available."
            )
    
    # Call USPTO
    result = await retrieval_service.search_patents(keywords, limit=request.limit)
    
    if not result.success:
        return RetrievalResponse(
            success=False,
            source="USPTO",
            candidates_stored=0,
            search_query=result.search_query,
            retrieval_notes="",
            error=result.error
        )
    
    # Store candidates
    stored = 0
    for candidate in result.candidates:
        evidence = CandidateEvidence(
            project_id=project_id,
            source_type="patent",
            title=candidate.title,
            authors=candidate.authors,
            abstract=candidate.abstract,
            source_name=EvidenceSource.USPTO,
            source_url=candidate.source_url,
            publication_date=candidate.publication_date,
            search_query=result.search_query
        )
        db.add(evidence)
        stored += 1
    
    # Update analysis state
    if db_project.analysis_state:
        db_project.analysis_state.evidence_retrieved = True
        notes = db_project.analysis_state.retrieval_notes or ""
        if "patents" not in notes.lower():
            db_project.analysis_state.retrieval_notes = f"{notes} Retrieved {stored} patents. No similarity scores computed."
    
    db.commit()
    
    return RetrievalResponse(
        success=True,
        source="USPTO",
        candidates_stored=stored,
        search_query=result.search_query,
        retrieval_notes=result.retrieval_notes
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/evidence",
    response_model=ProjectEvidenceResponse,
    tags=["Evidence Retrieval"]
)
def get_project_evidence(project_id: int, db: Session = Depends(get_db)):
    """
    Get all candidate evidence for a project.
    
    ⚠️ CANDIDATE EVIDENCE ONLY
    - No similarity scores
    - No novelty judgments
    - Just raw retrieved documents
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    evidence = db.query(CandidateEvidence).filter(
        CandidateEvidence.project_id == project_id
    ).all()
    
    papers = [e for e in evidence if e.source_type == "paper"]
    patents = [e for e in evidence if e.source_type == "patent"]
    
    return ProjectEvidenceResponse(
        project_id=project_id,
        papers=[EvidenceCandidateResponse(
            id=p.id,
            title=p.title,
            authors=p.authors,
            abstract=p.abstract,
            source_name=p.source_name.value,
            source_url=p.source_url,
            publication_date=p.publication_date,
            retrieved_at=p.retrieved_at
        ) for p in papers],
        patents=[EvidenceCandidateResponse(
            id=p.id,
            title=p.title,
            authors=p.authors,
            abstract=p.abstract,
            source_name=p.source_name.value,
            source_url=p.source_url,
            publication_date=p.publication_date,
            retrieved_at=p.retrieved_at
        ) for p in patents],
        total_evidence=len(evidence)
    )


# ============== AI Analysis Endpoints (Phase 2) ==============

@app.post(
    f"{settings.api_prefix}/analysis/clarify-idea",
    response_model=AIAssistanceResponse,
    tags=["AI Analysis"]
)
def clarify_idea(request: AIAssistanceRequest, db: Session = Depends(get_db)):
    """
    Clarify and restate an idea in clearer technical language.
    
    ⚠️ AI ASSISTANCE ONLY
    - This does NOT determine novelty
    - This is NOT legal advice
    - Human review is required
    """
    # Verify project exists
    db_project = crud.get_project(db, request.project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {request.project_id} not found"
        )
    
    # Call AI service
    result = ai_service.clarify_idea(request.text)
    
    # Update analysis state if successful
    if result.success and db_project.analysis_state:
        db_project.analysis_state.ai_explanations_generated = True
        db_project.analysis_state.last_ai_action = AIAction.CLARIFY_IDEA
        db_project.analysis_state.last_ai_timestamp = datetime.utcnow()
        db_project.analysis_state.analysis_status = AnalysisStatus.ASSISTIVE_ONLY
        db_project.analysis_state.notes = "AI has provided clarification assistance. This is advisory only."
        db.commit()
    
    return result


@app.post(
    f"{settings.api_prefix}/analysis/rewrite-text",
    response_model=AIAssistanceResponse,
    tags=["AI Analysis"]
)
def rewrite_text(request: AIAssistanceRequest, db: Session = Depends(get_db)):
    """
    Rewrite text to be more specific and technically clear.
    
    ⚠️ AI ASSISTANCE ONLY
    - This does NOT make text legally valid
    - This does NOT improve patentability
    - Human review is required
    """
    # Verify project exists
    db_project = crud.get_project(db, request.project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {request.project_id} not found"
        )
    
    # Call AI service with context
    context = request.context or "technical claim"
    result = ai_service.rewrite_text(request.text, context)
    
    # Update analysis state if successful
    if result.success and db_project.analysis_state:
        db_project.analysis_state.ai_explanations_generated = True
        db_project.analysis_state.last_ai_action = AIAction.REWRITE_TEXT
        db_project.analysis_state.last_ai_timestamp = datetime.utcnow()
        db_project.analysis_state.analysis_status = AnalysisStatus.ASSISTIVE_ONLY
        db_project.analysis_state.notes = "AI has provided rewriting assistance. This is advisory only."
        db.commit()
    
    return result


@app.post(
    f"{settings.api_prefix}/analysis/explain-risks",
    response_model=AIAssistanceResponse,
    tags=["AI Analysis"]
)
def explain_risks(request: AIAssistanceRequest, db: Session = Depends(get_db)):
    """
    Explain types of risks commonly associated with ideas in this domain.
    
    ⚠️ AI ASSISTANCE ONLY
    - This does NOT assess YOUR specific risk
    - This does NOT provide legal advice
    - This does NOT claim certainty about novelty
    - Human review is required
    """
    # Verify project exists
    db_project = crud.get_project(db, request.project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {request.project_id} not found"
        )
    
    # Call AI service with domain
    domain = db_project.domain or request.context or "technology"
    result = ai_service.explain_risks(request.text, domain)
    
    # Update analysis state if successful
    if result.success and db_project.analysis_state:
        db_project.analysis_state.ai_explanations_generated = True
        db_project.analysis_state.last_ai_action = AIAction.EXPLAIN_RISKS
        db_project.analysis_state.last_ai_timestamp = datetime.utcnow()
        db_project.analysis_state.analysis_status = AnalysisStatus.ASSISTIVE_ONLY
        db_project.analysis_state.notes = "AI has provided risk awareness. This is advisory only, not a specific assessment."
        db.commit()
    
    return result


# ============== Phase 4: Similarity & Novelty Endpoints ==============

@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/generate-embeddings",
    response_model=EmbeddingGenerationResponse,
    tags=["Similarity & Novelty"]
)
def generate_embeddings(project_id: int, db: Session = Depends(get_db)):
    """
    Generate embeddings for the user's idea and all evidence.
    
    Uses text-embedding-3-small model via OpenAI-compatible API.
    Embeddings are cached - recomputes only when text changes.
    
    ⚠️ Requires API key to be configured.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get idea text
    idea_text = db_project.idea_text
    if not idea_text:
        # Try extracted texts
        extracted = db.query(ExtractedText).filter(
            ExtractedText.project_id == project_id
        ).all()
        if extracted:
            idea_text = " ".join([e.content[:2000] for e in extracted])
    
    if not idea_text:
        return EmbeddingGenerationResponse(
            success=False,
            project_id=project_id,
            idea_embedded=False,
            evidence_embedded=0,
            total_evidence=0,
            notes="",
            error="No idea text or extracted text available."
        )
    
    # Generate idea embedding
    idea_hash = embedding_service.compute_text_hash(idea_text)
    existing_idea = db.query(IdeaEmbedding).filter(
        IdeaEmbedding.project_id == project_id
    ).first()
    
    idea_embedded = False
    if existing_idea and existing_idea.text_hash == idea_hash:
        idea_embedded = True  # Already cached
    else:
        result = embedding_service.generate_embedding(idea_text)
        if result.success:
            if existing_idea:
                existing_idea.embedding = embedding_service.embedding_to_json(result.embedding)
                existing_idea.text_hash = result.text_hash
                existing_idea.model_name = result.model_name
                existing_idea.dimensions = result.dimensions
                existing_idea.created_at = datetime.utcnow()
            else:
                new_embedding = IdeaEmbedding(
                    project_id=project_id,
                    embedding=embedding_service.embedding_to_json(result.embedding),
                    text_hash=result.text_hash,
                    model_name=result.model_name,
                    dimensions=result.dimensions
                )
                db.add(new_embedding)
            idea_embedded = True
        else:
            return EmbeddingGenerationResponse(
                success=False,
                project_id=project_id,
                idea_embedded=False,
                evidence_embedded=0,
                total_evidence=0,
                notes="",
                error=result.error
            )
    
    # Generate evidence embeddings
    evidence = db.query(CandidateEvidence).filter(
        CandidateEvidence.project_id == project_id
    ).all()
    
    evidence_embedded = 0
    for ev in evidence:
        ev_text = f"{ev.title}. {ev.abstract or ''}"
        ev_hash = embedding_service.compute_text_hash(ev_text)
        
        existing_ev = db.query(EvidenceEmbedding).filter(
            EvidenceEmbedding.evidence_id == ev.id
        ).first()
        
        if existing_ev and existing_ev.text_hash == ev_hash:
            evidence_embedded += 1
            continue
        
        result = embedding_service.generate_embedding(ev_text)
        if result.success:
            if existing_ev:
                existing_ev.embedding = embedding_service.embedding_to_json(result.embedding)
                existing_ev.text_hash = result.text_hash
                existing_ev.model_name = result.model_name
                existing_ev.dimensions = result.dimensions
                existing_ev.created_at = datetime.utcnow()
            else:
                new_ev_emb = EvidenceEmbedding(
                    evidence_id=ev.id,
                    embedding=embedding_service.embedding_to_json(result.embedding),
                    text_hash=result.text_hash,
                    model_name=result.model_name,
                    dimensions=result.dimensions
                )
                db.add(new_ev_emb)
            evidence_embedded += 1
    
    db.commit()
    
    return EmbeddingGenerationResponse(
        success=True,
        project_id=project_id,
        idea_embedded=idea_embedded,
        evidence_embedded=evidence_embedded,
        total_evidence=len(evidence),
        notes=f"Embeddings generated using {settings.embedding_model}."
    )


@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/compute-similarity",
    response_model=SimilarityComputationResponse,
    tags=["Similarity & Novelty"]
)
def compute_similarity(project_id: int, db: Session = Depends(get_db)):
    """
    Compute similarity between idea and all evidence.
    
    Uses cosine similarity on pre-generated embeddings.
    Results are DETERMINISTIC: same input → same output.
    
    ⚠️ Requires embeddings to be generated first.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get idea embedding
    idea_emb = db.query(IdeaEmbedding).filter(
        IdeaEmbedding.project_id == project_id
    ).first()
    
    if not idea_emb:
        return SimilarityComputationResponse(
            success=False,
            project_id=project_id,
            scores_computed=0,
            max_score=None,
            notes="",
            error="Idea embedding not found. Generate embeddings first."
        )
    
    idea_vector = embedding_service.embedding_from_json(idea_emb.embedding)
    
    # Get all evidence with embeddings
    evidence = db.query(CandidateEvidence).filter(
        CandidateEvidence.project_id == project_id
    ).all()
    
    scores_computed = 0
    max_score = 0.0
    
    for ev in evidence:
        ev_emb = db.query(EvidenceEmbedding).filter(
            EvidenceEmbedding.evidence_id == ev.id
        ).first()
        
        if not ev_emb:
            continue
        
        ev_vector = embedding_service.embedding_from_json(ev_emb.embedding)
        
        # Compute cosine similarity
        score = similarity_engine.cosine_similarity(idea_vector, ev_vector)
        score_int = int(score * 10000)  # Store as int for precision
        
        # Update or create similarity score
        existing_score = db.query(SimilarityScore).filter(
            SimilarityScore.project_id == project_id,
            SimilarityScore.evidence_id == ev.id
        ).first()
        
        if existing_score:
            existing_score.score = score_int
            existing_score.computed_at = datetime.utcnow()
        else:
            new_score = SimilarityScore(
                project_id=project_id,
                evidence_id=ev.id,
                score=score_int,
                evidence_type=ev.source_type
            )
            db.add(new_score)
        
        scores_computed += 1
        max_score = max(max_score, score)
    
    # Update analysis state
    if db_project.analysis_state:
        db_project.analysis_state.similarity_computed = True
        db_project.analysis_state.max_similarity_score = int(max_score * 10000)
    
    db.commit()
    
    return SimilarityComputationResponse(
        success=True,
        project_id=project_id,
        scores_computed=scores_computed,
        max_score=max_score if scores_computed > 0 else None,
        notes=f"Computed {scores_computed} similarity scores. Max: {max_score:.4f}"
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/novelty-risk",
    response_model=NoveltyRiskResponse,
    tags=["Similarity & Novelty"]
)
def get_novelty_risk(project_id: int, db: Session = Depends(get_db)):
    """
    Get novelty risk assessment for a project.
    
    Classification based on MAX similarity score:
    - GREEN: Low overlap (< 0.50 research, < 0.45 patent)
    - YELLOW: Partial overlap (0.50-0.79 research, 0.45-0.74 patent)
    - RED: High overlap (≥ 0.80 research, ≥ 0.75 patent)
    - UNKNOWN: No evidence to compare
    
    ⚠️ Every risk is traceable to specific evidence.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get all similarity scores
    scores = db.query(SimilarityScore).filter(
        SimilarityScore.project_id == project_id
    ).all()
    
    if not scores:
        # Update analysis state
        if db_project.analysis_state:
            db_project.analysis_state.novelty_risk = NoveltyRiskLevelModel.UNKNOWN
            db.commit()
        
        return NoveltyRiskResponse(
            project_id=project_id,
            novelty_risk=NoveltyRiskLevel.UNKNOWN,
            max_similarity_score=None,
            top_match=None,
            research_risk=NoveltyRiskLevel.UNKNOWN,
            research_max_score=None,
            research_matches=0,
            patent_risk=NoveltyRiskLevel.UNKNOWN,
            patent_max_score=None,
            patent_matches=0,
            total_evidence_compared=0,
            notes="Insufficient evidence to assess novelty risk."
        )
    
    # Separate by type
    research_scores = [s for s in scores if s.evidence_type == "paper"]
    patent_scores = [s for s in scores if s.evidence_type == "patent"]
    
    # Compute risk for each type
    research_max = max([s.score_float for s in research_scores]) if research_scores else None
    patent_max = max([s.score_float for s in patent_scores]) if patent_scores else None
    
    research_risk = (
        similarity_engine.classify_novelty_risk(research_max, "paper")
        if research_max is not None
        else similarity_engine.NoveltyRisk.UNKNOWN
    )
    patent_risk = (
        similarity_engine.classify_novelty_risk(patent_max, "patent")
        if patent_max is not None
        else similarity_engine.NoveltyRisk.UNKNOWN
    )
    
    # Overall risk (max of both)
    all_scores_float = [s.score_float for s in scores]
    max_score = max(all_scores_float)
    
    # Find top match
    top_score = max(scores, key=lambda s: s.score)
    top_evidence = db.query(CandidateEvidence).filter(
        CandidateEvidence.id == top_score.evidence_id
    ).first()
    
    overall_risk = similarity_engine.classify_novelty_risk(max_score, top_score.evidence_type)
    
    # Build top match response
    top_match = None
    if top_evidence:
        top_match = SimilarityMatch(
            evidence_id=top_evidence.id,
            title=top_evidence.title,
            authors=top_evidence.authors,
            source=top_evidence.source_name.value,
            source_url=top_evidence.source_url,
            evidence_type=top_evidence.source_type,
            similarity_score=top_score.score_float
        )
    
    # Generate notes
    if overall_risk == similarity_engine.NoveltyRisk.RED:
        notes = f"High similarity detected ({max_score:.2f}). Significant overlap with '{top_evidence.title[:50]}...'."
    elif overall_risk == similarity_engine.NoveltyRisk.YELLOW:
        notes = f"Moderate similarity detected ({max_score:.2f}). Review recommended."
    else:
        notes = f"Low similarity detected ({max_score:.2f}). Idea appears to have novel aspects."
    
    # Update analysis state
    if db_project.analysis_state:
        db_project.analysis_state.novelty_risk = NoveltyRiskLevelModel(overall_risk.value)
        db_project.analysis_state.max_similarity_score = int(max_score * 10000)
        db_project.analysis_state.top_evidence_id = top_evidence.id if top_evidence else None
        db_project.analysis_state.notes = notes
        db.commit()
    
    return NoveltyRiskResponse(
        project_id=project_id,
        novelty_risk=NoveltyRiskLevel(overall_risk.value),
        max_similarity_score=max_score,
        top_match=top_match,
        research_risk=NoveltyRiskLevel(research_risk.value),
        research_max_score=research_max,
        research_matches=len(research_scores),
        patent_risk=NoveltyRiskLevel(patent_risk.value),
        patent_max_score=patent_max,
        patent_matches=len(patent_scores),
        total_evidence_compared=len(scores),
        notes=notes
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/similarity-scores",
    response_model=SimilarityListResponse,
    tags=["Similarity & Novelty"]
)
def list_similarity_scores(
    project_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List all similarity scores for a project, sorted by similarity.
    
    Each score is linked to specific evidence with verifiable URL.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    scores = db.query(SimilarityScore).filter(
        SimilarityScore.project_id == project_id
    ).order_by(SimilarityScore.score.desc()).limit(limit).all()
    
    matches = []
    for s in scores:
        evidence = db.query(CandidateEvidence).filter(
            CandidateEvidence.id == s.evidence_id
        ).first()
        
        if evidence:
            matches.append(SimilarityMatch(
                evidence_id=evidence.id,
                title=evidence.title,
                authors=evidence.authors,
                source=evidence.source_name.value,
                source_url=evidence.source_url,
                evidence_type=evidence.source_type,
                similarity_score=s.score_float
            ))
    
    return SimilarityListResponse(
        project_id=project_id,
        matches=matches,
        total=len(matches)
    )


# ============== Phase 5: Comparative Analysis Endpoints ==============

@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/generate-comparison",
    response_model=ComparativeAnalysisResponse,
    tags=["Comparative Analysis"]
)
def generate_comparison(
    project_id: int,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """
    Generate evidence-grounded comparative analysis.
    
    Explains WHY the novelty risk is what it is.
    
    HARD RULES:
    - Every claim traces to real evidence
    - Uncertainty language is REQUIRED
    - LLM cannot override similarity scores
    - Limitations are always stated
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get idea text
    idea_text = db_project.idea_text
    if not idea_text:
        extracted = db.query(ExtractedText).filter(
            ExtractedText.project_id == project_id
        ).first()
        if extracted:
            idea_text = extracted.content[:3000]
    
    if not idea_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No idea text available. Add idea text or extract from files first."
        )
    
    # Get top similarity scores
    scores = db.query(SimilarityScore).filter(
        SimilarityScore.project_id == project_id
    ).order_by(SimilarityScore.score.desc()).limit(top_k).all()
    
    if not scores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No similarity scores found. Compute similarity first."
        )
    
    # Build evidence items for comparison
    evidence_items = []
    evidence_summaries = []
    research_count = 0
    patent_count = 0
    
    for s in scores:
        ev = db.query(CandidateEvidence).filter(
            CandidateEvidence.id == s.evidence_id
        ).first()
        if ev:
            evidence_items.append({
                "id": ev.id,
                "title": ev.title,
                "source": ev.source_name.value,
                "source_url": ev.source_url,
                "abstract": ev.abstract or "",
                "similarity": s.score_float,
                "type": ev.source_type
            })
            if ev.source_type == "paper":
                research_count += 1
            else:
                patent_count += 1
    
    # Get current novelty risk
    overall_risk = "UNKNOWN"
    max_similarity = 0.0
    if db_project.analysis_state:
        overall_risk = db_project.analysis_state.novelty_risk.value
        if db_project.analysis_state.max_similarity_score:
            max_similarity = db_project.analysis_state.max_similarity_score / 10000.0
    
    # Generate multi-evidence comparison
    analysis_result = comparative_service.generate_multi_evidence_comparison(
        idea_text=idea_text,
        evidence_items=evidence_items,
        overall_risk=overall_risk,
        max_similarity=max_similarity
    )
    
    if not analysis_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparative analysis failed: {analysis_result.get('error', 'Unknown error')}"
        )
    
    # Build limitations
    limitations = comparative_service.build_limitations_section(
        evidence_count=len(evidence_items),
        research_count=research_count,
        patent_count=patent_count,
        max_similarity=max_similarity
    )
    
    # Add any from LLM response
    if "limitations" in analysis_result:
        limitations.extend(analysis_result.get("limitations", []))
    
    # Get next version number
    last_analysis = db.query(ComparativeAnalysis).filter(
        ComparativeAnalysis.project_id == project_id
    ).order_by(ComparativeAnalysis.version.desc()).first()
    next_version = (last_analysis.version + 1) if last_analysis else 1
    
    # Store in database
    new_analysis = ComparativeAnalysis(
        project_id=project_id,
        version=next_version,
        evidence_ids=json.dumps([e["id"] for e in evidence_items]),
        existing_work_summary=analysis_result.get("existing_landscape", ""),
        overlap_analysis=json.dumps(analysis_result.get("key_overlaps", [])),
        differentiation_analysis=json.dumps(analysis_result.get("potential_differentiators", [])),
        novelty_explanation=analysis_result.get("risk_explanation", ""),
        limitations=json.dumps(limitations),
        confidence_level=analysis_result.get("confidence_level", "medium"),
        input_novelty_risk=overall_risk,
        input_max_similarity=int(max_similarity * 10000)
    )
    db.add(new_analysis)
    
    # Update analysis state
    if db_project.analysis_state:
        db_project.analysis_state.comparison_generated = True
        db_project.analysis_state.comparison_version = next_version
    
    db.commit()
    
    # Build evidence summaries for response
    for ev in evidence_items:
        evidence_summaries.append(EvidenceSummaryItem(
            evidence_id=ev["id"],
            title=ev["title"],
            source=ev["source"],
            source_url=ev["source_url"],
            similarity_score=ev["similarity"],
            summary=f"Evidence with {ev['similarity']:.2f} similarity"
        ))
    
    # Build overlap and difference points
    overlap_points = []
    for overlap in analysis_result.get("key_overlaps", []):
        if isinstance(overlap, dict):
            overlap_points.append(OverlapPoint(
                idea_concept=overlap.get("concept", ""),
                evidence_concept=", ".join(overlap.get("evidence_titles", [])),
                evidence_id=None,
                evidence_title=None
            ))
    
    difference_points = []
    for diff in analysis_result.get("potential_differentiators", []):
        if isinstance(diff, dict):
            difference_points.append(DifferencePoint(
                aspect=diff.get("aspect", ""),
                description=diff.get("description", ""),
                uncertainty=diff.get("uncertainty", "Requires verification")
            ))
    
    return ComparativeAnalysisResponse(
        project_id=project_id,
        version=next_version,
        novelty_risk=NoveltyRiskLevel(overall_risk),
        max_similarity=max_similarity,
        evidence_summaries=evidence_summaries,
        existing_landscape=analysis_result.get("existing_landscape", ""),
        overlap_points=overlap_points,
        difference_points=difference_points,
        novelty_explanation=analysis_result.get("risk_explanation", ""),
        limitations=limitations,
        confidence_level=analysis_result.get("confidence_level", "medium"),
        recommendation=analysis_result.get("recommendation", "Human expert review recommended."),
        evidence_count=len(evidence_items),
        research_count=research_count,
        patent_count=patent_count,
        generated_at=datetime.utcnow().isoformat()
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/comparison",
    response_model=ComparativeAnalysisResponse,
    tags=["Comparative Analysis"]
)
def get_comparison(project_id: int, db: Session = Depends(get_db)):
    """
    Get latest comparative analysis for a project.
    
    Returns the most recent version of evidence-grounded analysis.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get latest analysis
    analysis = db.query(ComparativeAnalysis).filter(
        ComparativeAnalysis.project_id == project_id
    ).order_by(ComparativeAnalysis.version.desc()).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No comparative analysis found. Generate one first."
        )
    
    # Parse stored JSON fields
    evidence_ids = json.loads(analysis.evidence_ids) if analysis.evidence_ids else []
    overlap_raw = json.loads(analysis.overlap_analysis) if analysis.overlap_analysis else []
    diff_raw = json.loads(analysis.differentiation_analysis) if analysis.differentiation_analysis else []
    limitations = json.loads(analysis.limitations) if analysis.limitations else []
    
    # Build evidence summaries
    evidence_summaries = []
    research_count = 0
    patent_count = 0
    for ev_id in evidence_ids:
        ev = db.query(CandidateEvidence).filter(CandidateEvidence.id == ev_id).first()
        score = db.query(SimilarityScore).filter(
            SimilarityScore.project_id == project_id,
            SimilarityScore.evidence_id == ev_id
        ).first()
        if ev:
            evidence_summaries.append(EvidenceSummaryItem(
                evidence_id=ev.id,
                title=ev.title,
                source=ev.source_name.value,
                source_url=ev.source_url,
                similarity_score=score.score_float if score else 0.0,
                summary=f"Retrieved from {ev.source_name.value}"
            ))
            if ev.source_type == "paper":
                research_count += 1
            else:
                patent_count += 1
    
    # Build overlap points
    overlap_points = []
    for overlap in overlap_raw:
        if isinstance(overlap, dict):
            overlap_points.append(OverlapPoint(
                idea_concept=overlap.get("concept", ""),
                evidence_concept=", ".join(overlap.get("evidence_titles", [])),
                evidence_id=None,
                evidence_title=None
            ))
    
    # Build difference points
    difference_points = []
    for diff in diff_raw:
        if isinstance(diff, dict):
            difference_points.append(DifferencePoint(
                aspect=diff.get("aspect", ""),
                description=diff.get("description", ""),
                uncertainty=diff.get("uncertainty", "Requires verification")
            ))
    
    return ComparativeAnalysisResponse(
        project_id=project_id,
        version=analysis.version,
        novelty_risk=NoveltyRiskLevel(analysis.input_novelty_risk),
        max_similarity=analysis.input_max_similarity / 10000.0 if analysis.input_max_similarity else None,
        evidence_summaries=evidence_summaries,
        existing_landscape=analysis.existing_work_summary or "",
        overlap_points=overlap_points,
        difference_points=difference_points,
        novelty_explanation=analysis.novelty_explanation or "",
        limitations=limitations,
        confidence_level=analysis.confidence_level or "medium",
        recommendation="Human expert review recommended.",
        evidence_count=len(evidence_ids),
        research_count=research_count,
        patent_count=patent_count,
        generated_at=analysis.created_at.isoformat()
    )


# ============== Phase 6: Draft Optimization Endpoints ==============

@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/draft-optimize",
    response_model=DraftOptimizeResponse,
    tags=["Draft Optimization"]
)
def optimize_draft(
    project_id: int,
    request: DraftOptimizeRequest,
    db: Session = Depends(get_db)
):
    """
    Generate localized draft improvement suggestions.
    
    HARD RULES:
    - NO full document rewrites
    - NO new technical claims injected
    - NO claims of novelty improvement
    - Suggestions are LOCALIZED and REJECTABLE
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    draft_text = request.draft_text
    
    # Get overlap context from latest comparative analysis if available
    overlap_context = None
    novelty_risk = "UNKNOWN"
    
    latest_analysis = db.query(ComparativeAnalysis).filter(
        ComparativeAnalysis.project_id == project_id
    ).order_by(ComparativeAnalysis.version.desc()).first()
    
    if latest_analysis:
        analysis_data = {
            "existing_landscape": latest_analysis.existing_work_summary,
            "key_overlaps": json.loads(latest_analysis.overlap_analysis) if latest_analysis.overlap_analysis else [],
            "potential_differentiators": json.loads(latest_analysis.differentiation_analysis) if latest_analysis.differentiation_analysis else []
        }
        overlap_context = draft_service.build_overlap_context_from_analysis(analysis_data)
        novelty_risk = latest_analysis.input_novelty_risk
    
    # Generate suggestions using LLM
    result = draft_service.generate_draft_suggestions(
        draft_text=draft_text,
        overlap_context=overlap_context,
        novelty_risk=novelty_risk
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Draft optimization failed: {result.get('error', 'Unknown error')}"
        )
    
    # Get next version number
    last_draft = db.query(DraftVersion).filter(
        DraftVersion.project_id == project_id
    ).order_by(DraftVersion.version.desc()).first()
    next_version = (last_draft.version + 1) if last_draft else 1
    
    # Store draft version
    new_draft = DraftVersion(
        project_id=project_id,
        version=next_version,
        original_text=draft_text
    )
    db.add(new_draft)
    db.flush()  # Get the ID
    
    # Store suggestions
    suggestion_items = []
    for s in result["suggestions"]:
        new_suggestion = DraftSuggestion(
            draft_version_id=new_draft.id,
            original_snippet=s["original_text_snippet"],
            suggested_revision=s["suggested_revision"],
            reason=s["reason_for_change"],
            change_type=ChangeTypeModel(s["change_type"]),
            preserves_intent=PreservesIntentModel(s["preserves_intent"]),
            status=SuggestionStatusModel.PENDING,
            start_position=s.get("start_position"),
            end_position=s.get("end_position")
        )
        db.add(new_suggestion)
        db.flush()
        
        suggestion_items.append(DraftSuggestionItem(
            id=new_suggestion.id,
            original_text_snippet=s["original_text_snippet"],
            suggested_revision=s["suggested_revision"],
            reason_for_change=s["reason_for_change"],
            change_type=ChangeType(s["change_type"]),
            preserves_intent=PreservesIntent(s["preserves_intent"]),
            status=SuggestionStatus.PENDING,
            start_position=s.get("start_position"),
            end_position=s.get("end_position")
        ))
    
    # Update analysis state
    if db_project.analysis_state:
        db_project.analysis_state.notes = f"Draft optimization v{next_version} generated with {len(suggestion_items)} suggestions."
    
    db.commit()
    
    # Phase 10: Audit Log
    audit_service.log_action(
        db, 
        "DRAFT_OPTIMIZED", 
        "DraftVersion", 
        new_draft.id, 
        None,
        metadata={
             "suggestions_count": len(suggestion_items),
             "model": settings.llm_model,
             "project_id": project_id
        }
    )
    
    return DraftOptimizeResponse(
        success=True,
        project_id=project_id,
        draft_version_id=new_draft.id,
        version=next_version,
        suggestions=suggestion_items,
        total_suggestions=len(suggestion_items),
        limitations=draft_service.build_limitations(),
        disclaimer=draft_service.DRAFT_DISCLAIMER
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/draft-versions",
    response_model=DraftHistoryResponse,
    tags=["Draft Optimization"]
)
def get_draft_history(project_id: int, db: Session = Depends(get_db)):
    """
    Get all draft versions for a project.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    drafts = db.query(DraftVersion).filter(
        DraftVersion.project_id == project_id
    ).order_by(DraftVersion.version.desc()).all()
    
    versions = []
    for draft in drafts:
        suggestions = db.query(DraftSuggestion).filter(
            DraftSuggestion.draft_version_id == draft.id
        ).all()
        
        pending = sum(1 for s in suggestions if s.status == SuggestionStatusModel.PENDING)
        accepted = sum(1 for s in suggestions if s.status == SuggestionStatusModel.ACCEPTED)
        rejected = sum(1 for s in suggestions if s.status == SuggestionStatusModel.REJECTED)
        
        versions.append(DraftVersionResponse(
            id=draft.id,
            project_id=draft.project_id,
            version=draft.version,
            original_text=draft.original_text[:500] + "..." if len(draft.original_text) > 500 else draft.original_text,
            suggestions_count=len(suggestions),
            pending_count=pending,
            accepted_count=accepted,
            rejected_count=rejected,
            created_at=draft.created_at
        ))
    
    return DraftHistoryResponse(
        project_id=project_id,
        versions=versions,
        total=len(versions)
    )


@app.put(
    f"{settings.api_prefix}/suggestions/{{suggestion_id}}",
    response_model=SuggestionUpdateResponse,
    tags=["Draft Optimization"]
)
def update_suggestion_status(
    suggestion_id: int,
    request: SuggestionUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Accept or reject a draft suggestion.
    """
    suggestion = db.query(DraftSuggestion).filter(
        DraftSuggestion.id == suggestion_id
    ).first()
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suggestion with id {suggestion_id} not found"
        )
    
    old_status = suggestion.status
    suggestion.status = SuggestionStatusModel(request.status.value)
    db.commit()
    
    status_messages = {
        SuggestionStatus.ACCEPTED: "Suggestion accepted. You may apply this change to your document.",
        SuggestionStatus.REJECTED: "Suggestion rejected. It will not be applied.",
        SuggestionStatus.PENDING: "Suggestion marked as pending for later review."
    }
    
    return SuggestionUpdateResponse(
        success=True,
        suggestion_id=suggestion_id,
        new_status=request.status,
        message=status_messages.get(request.status, "Status updated.")
    )


# ============== Phase 7: Venue Recommendation Endpoints ==============

@app.post(
    f"{settings.api_prefix}/recommendations/venues",
    response_model=VenueRecommendationResponse,
    tags=["Venue Recommendations"]
)
def get_venue_recommendations(
    request: VenueRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get venue recommendations for a project.
    
    ⚠️ SUGGESTIONS ONLY
    - These are NOT predictions of acceptance
    - No guarantee of acceptance implied
    - Based on topic matching and novelty risk
    - Always includes limitations
    """
    db_project = crud.get_project(db, request.project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {request.project_id} not found"
        )
    
    # Get project characteristics
    project_type = db_project.type.value if db_project.type else "RESEARCH"
    domain = db_project.domain
    
    # Get novelty risk from analysis state
    novelty_risk = "UNKNOWN"
    if db_project.analysis_state:
        novelty_risk = db_project.analysis_state.novelty_risk.value
    
    # Check if draft exists
    has_draft = bool(db_project.idea_text) or db.query(DraftVersion).filter(
        DraftVersion.project_id == request.project_id
    ).first() is not None
    
    # Get evidence count
    evidence_count = db.query(CandidateEvidence).filter(
        CandidateEvidence.project_id == request.project_id
    ).count()
    
    # Extract keywords from idea text or extracted texts
    keywords = []
    if db_project.idea_text:
        # Simple keyword extraction from idea text
        keywords = [w.strip().lower() for w in db_project.idea_text.split() if len(w) > 4][:20]
    else:
        # Try extracted texts
        extracted = db.query(ExtractedText).filter(
            ExtractedText.project_id == request.project_id
        ).all()
        if extracted:
            text = " ".join([e.content[:1000] for e in extracted])
            keywords = [w.strip().lower() for w in text.split() if len(w) > 4][:20]
    
    # Generate recommendations
    result = recommendation_service.generate_recommendations(
        keywords=keywords,
        project_type=project_type,
        novelty_risk=novelty_risk,
        has_draft=has_draft,
        evidence_count=evidence_count,
        domain=domain,
        max_recommendations=10
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {result.error}"
        )
    
    # Build response
    venue_items = [
        VenueRecommendationItem(
            name=v.name,
            short_name=v.short_name,
            venue_type=VenueTypeSchema(v.venue_type) if not isinstance(v.venue_type, str) else VenueTypeSchema(v.venue_type),
            domains=v.domains,
            relevance_reason=v.relevance_reason,
            submission_formats=v.submission_formats,
            match_strength=v.match_strength,
            cautions=v.cautions
        )
        for v in result.venues
    ]
    
    readiness = ReadinessNotesResponse(
        level=ReadinessLevel(result.readiness.level.value),
        explanation=result.readiness.explanation,
        suggestions=result.readiness.suggestions
    )
    
    return VenueRecommendationResponse(
        success=True,
        project_id=request.project_id,
        venues=venue_items,
        readiness=readiness,
        general_guidance=result.general_guidance,
        limitations=result.limitations,
        disclaimer=recommendation_service.RECOMMENDATION_DISCLAIMER,
        keyword_count=len(keywords),
        evidence_count=evidence_count,
        novelty_risk=NoveltyRiskLevel(novelty_risk)
    )


# ============== Phase 8: Patent Claim Structuring Endpoints ==============

@app.post(
    f"{settings.api_prefix}/projects/{{project_id}}/claims/generate",
    response_model=ClaimGenerationResponse,
    tags=["Patent Claims"]
)
def generate_claims(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate patent claim structure for a project.
    
    ⚠️ CONCEPTUAL DRAFTS ONLY - NOT LEGAL ADVICE
    
    This endpoint is ONLY available for PATENT projects.
    All outputs include legal disclaimers.
    
    NEVER asserts patentability or legal validity.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
        
    # Phase 10: Compliance Check
    compliance_service.validate_feature_access("PATENT_CLAIM_GENERATION")
    
    # Verify project type is PATENT
    if db_project.type != ProjectType.PATENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim generation is only available for PATENT projects. This project is type: " + db_project.type.value
        )
    
    # Verify idea text exists
    if not db_project.idea_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project must have idea text before generating claims."
        )
    
    # Get overlap context from comparative analysis if available
    overlap_context = None
    novelty_risk = "UNKNOWN"
    
    latest_analysis = db.query(ComparativeAnalysis).filter(
        ComparativeAnalysis.project_id == project_id
    ).order_by(ComparativeAnalysis.version.desc()).first()
    
    if latest_analysis:
        analysis_data = {
            "existing_work_summary": latest_analysis.existing_work_summary,
            "overlaps": json.loads(latest_analysis.overlap_analysis) if latest_analysis.overlap_analysis else [],
            "differentiators": json.loads(latest_analysis.differentiation_analysis) if latest_analysis.differentiation_analysis else []
        }
        overlap_context = claim_service.build_overlap_context(analysis_data)
        novelty_risk = latest_analysis.input_novelty_risk
    
    # Generate claims
    result = claim_service.generate_claim_structure(
        idea_text=db_project.idea_text,
        overlap_context=overlap_context,
        novelty_risk=novelty_risk
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Claim generation failed: {result.error}"
        )
    
    # Get next version number
    last_claim = db.query(ClaimDraft).filter(
        ClaimDraft.project_id == project_id
    ).order_by(ClaimDraft.version.desc()).first()
    next_version = (last_claim.version + 1) if last_claim else 1
    
    # Store generation metadata
    gen_metadata = ClaimGenerationMetadata(
        project_id=project_id,
        model_used=settings.llm_model,
        prompt_version=claim_service.PROMPT_VERSION,
        input_hash=result.input_hash,
        claims_generated=len(result.claims),
        independent_claims=sum(1 for c in result.claims if c.claim_type == "INDEPENDENT"),
        dependent_claims=sum(1 for c in result.claims if c.claim_type == "DEPENDENT")
    )
    db.add(gen_metadata)
    db.flush()
    
    # Store claims
    claim_id_mapping = {}  # old claim_number -> new db id
    claim_items = []
    
    for c in result.claims:
        new_claim = ClaimDraft(
            project_id=project_id,
            version=next_version,
            claim_number=c.claim_number,
            claim_type=ClaimTypeModel(c.claim_type),
            claim_text=c.claim_text,
            technical_feature=c.technical_feature,
            explanation=c.explanation,
            parent_claim_id=None  # Set after first pass
        )
        db.add(new_claim)
        db.flush()
        claim_id_mapping[c.claim_number] = new_claim.id
        
        claim_items.append(ClaimDraftItem(
            id=new_claim.id,
            claim_number=c.claim_number,
            claim_type=ClaimTypeSchema(c.claim_type),
            claim_text=c.claim_text,
            technical_feature=c.technical_feature,
            explanation=c.explanation,
            parent_claim_number=c.parent_claim_number
        ))
    
    # Second pass: set parent claim ids
    for c in result.claims:
        if c.parent_claim_number and c.parent_claim_number in claim_id_mapping:
            claim = db.query(ClaimDraft).filter(
                ClaimDraft.id == claim_id_mapping[c.claim_number]
            ).first()
            if claim:
                claim.parent_claim_id = claim_id_mapping[c.parent_claim_number]
    
    # Store risk annotations
    risk_items = []
    for r in result.risks:
        if r.claim_number in claim_id_mapping:
            new_risk = ClaimRiskAnnotation(
                claim_id=claim_id_mapping[r.claim_number],
                risk_type=ClaimRiskTypeModel(r.risk_type),
                description=r.description,
                evidence_id=r.evidence_id
            )
            db.add(new_risk)
            db.flush()
            
            risk_items.append(ClaimRiskAnnotationItem(
                id=new_risk.id,
                claim_number=r.claim_number,
                risk_type=ClaimRiskTypeSchema(r.risk_type),
                description=r.description,
                evidence_id=r.evidence_id
            ))
    
    db.commit()
    
    # Phase 10: Audit Log
    audit_service.log_action(
        db, 
        "CLAIMS_GENERATED", 
        "Project", 
        project_id, 
        None,
        metadata={
            "claims_count": len(result.claims),
            "novelty_risk": novelty_risk.value,
            "prompt_version": claim_service.PROMPT_VERSION
        }
    )
    
    # Build dependency graph
    graph = claim_service.build_dependency_graph(result.claims)
    
    # Build attorney handoff notes
    independent_count = sum(1 for c in result.claims if c.claim_type == "INDEPENDENT")
    dependent_count = sum(1 for c in result.claims if c.claim_type == "DEPENDENT")
    
    handoff = AttorneyHandoffNotes(
        independent_claims=independent_count,
        dependent_claims=dependent_count,
        review_areas=result.review_areas,
        prior_art_notes=overlap_context[:500] if overlap_context else "Prior art analysis not performed.",
        novelty_risk=novelty_risk,
        risk_recommendation=claim_service.get_risk_recommendation(novelty_risk),
        raw_text=result.attorney_handoff
    )
    
    return ClaimGenerationResponse(
        success=True,
        project_id=project_id,
        claims=claim_items,
        risks=risk_items,
        dependency_graph=ClaimDependencyGraph(
            nodes=graph["nodes"],
            edges=[ClaimDependencyEdge(from_claim=e["from"], to_claim=e["to"], label=e["label"]) for e in graph["edges"]],
            root_claims=graph["root_claims"]
        ),
        attorney_handoff=handoff,
        disclaimer=claim_service.LEGAL_DISCLAIMER,
        version=next_version,
        generation_id=gen_metadata.id
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/claims",
    response_model=ClaimsListResponse,
    tags=["Patent Claims"]
)
def list_claims(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    List all claims for a project.
    
    Returns claims with risk annotations.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    claims = db.query(ClaimDraft).filter(
        ClaimDraft.project_id == project_id
    ).order_by(ClaimDraft.version.desc(), ClaimDraft.claim_number).all()
    
    claim_items = []
    for c in claims:
        parent_num = None
        if c.parent_claim:
            parent_num = c.parent_claim.claim_number
            
        claim_items.append(ClaimDraftItem(
            id=c.id,
            claim_number=c.claim_number,
            claim_type=ClaimTypeSchema(c.claim_type.value),
            claim_text=c.claim_text,
            technical_feature=c.technical_feature or "",
            explanation=c.explanation or "",
            parent_claim_number=parent_num,
            is_flagged=c.is_flagged,
            flag_type=ClaimFlagTypeSchema(c.flag_type.value) if c.flag_type else None,
            flag_notes=c.flag_notes
        ))
    
    # Get risk annotations
    claim_ids = [c.id for c in claims]
    risks = db.query(ClaimRiskAnnotation).filter(
        ClaimRiskAnnotation.claim_id.in_(claim_ids)
    ).all() if claim_ids else []
    
    risk_items = []
    for r in risks:
        claim = next((c for c in claims if c.id == r.claim_id), None)
        risk_items.append(ClaimRiskAnnotationItem(
            id=r.id,
            claim_number=claim.claim_number if claim else 0,
            risk_type=ClaimRiskTypeSchema(r.risk_type.value),
            description=r.description,
            evidence_id=r.evidence_id
        ))
    
    return ClaimsListResponse(
        project_id=project_id,
        claims=claim_items,
        risks=risk_items,
        total_claims=len(claims),
        disclaimer=claim_service.LEGAL_DISCLAIMER
    )


@app.put(
    f"{settings.api_prefix}/claims/{{claim_id}}",
    response_model=ClaimUpdateResponse,
    tags=["Patent Claims"]
)
def update_claim(
    claim_id: int,
    request: ClaimUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update a claim's text.
    
    Creates a new version of the claim (immutable versioning).
    """
    claim = db.query(ClaimDraft).filter(ClaimDraft.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id {claim_id} not found"
        )
    
    if claim.is_immutable:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This claim is immutable and cannot be edited."
        )
    
    # Create new version
    new_claim = ClaimDraft(
        project_id=claim.project_id,
        version=claim.version + 1,
        claim_number=claim.claim_number,
        claim_type=claim.claim_type,
        claim_text=request.claim_text,
        technical_feature=request.technical_feature or claim.technical_feature,
        explanation=request.explanation or claim.explanation,
        parent_claim_id=claim.parent_claim_id,
        user_edited=True
    )
    db.add(new_claim)
    
    # Mark old claim as immutable
    claim.is_immutable = True
    
    db.commit()
    
    return ClaimUpdateResponse(
        success=True,
        claim_id=new_claim.id,
        new_version=new_claim.version,
        message="Claim updated. New version created."
    )


@app.post(
    f"{settings.api_prefix}/claims/{{claim_id}}/flag",
    response_model=ClaimFlagResponse,
    tags=["Patent Claims"]
)
def flag_claim(
    claim_id: int,
    request: ClaimFlagRequest,
    db: Session = Depends(get_db)
):
    """
    Flag a claim for review.
    
    Allows users to mark claims with concerns.
    """
    claim = db.query(ClaimDraft).filter(ClaimDraft.id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with id {claim_id} not found"
        )
    
    claim.is_flagged = True
    claim.flag_type = ClaimFlagTypeModel(request.flag_type.value)
    claim.flag_notes = request.notes
    
    db.commit()
    
    return ClaimFlagResponse(
        success=True,
        claim_id=claim_id,
        message=f"Claim flagged as {request.flag_type.value}."
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/claims/graph",
    tags=["Patent Claims"]
)
def get_claims_graph(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get dependency graph for claims.
    
    Returns visualization-ready graph structure.
    """
    db_project = crud.get_project(db, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    # Get latest version claims
    latest_version = db.query(ClaimDraft.version).filter(
        ClaimDraft.project_id == project_id
    ).order_by(ClaimDraft.version.desc()).first()
    
    if not latest_version:
        return {
            "nodes": [],
            "edges": [],
            "root_claims": [],
            "disclaimer": claim_service.LEGAL_DISCLAIMER
        }
    
    claims = db.query(ClaimDraft).filter(
        ClaimDraft.project_id == project_id,
        ClaimDraft.version == latest_version[0]
    ).order_by(ClaimDraft.claim_number).all()
    
    nodes = []
    edges = []
    root_claims = []
    
    for c in claims:
        nodes.append({
            "id": c.claim_number,
            "label": f"Claim {c.claim_number}",
            "type": c.claim_type.value,
            "text_preview": c.claim_text[:100] + "..." if len(c.claim_text) > 100 else c.claim_text
        })
        
        if c.parent_claim:
            edges.append({
                "from": c.parent_claim.claim_number,
                "to": c.claim_number,
                "label": "depends on"
            })
        
        if c.claim_type == ClaimTypeModel.INDEPENDENT:
            root_claims.append(c.claim_number)
    
    return {
        "nodes": nodes,
        "edges": edges,
        "root_claims": root_claims,
        "disclaimer": claim_service.LEGAL_DISCLAIMER
    }


# ============== Phase 9: Feedback & Confidence Endpoints ==============

@app.post(
    f"{settings.api_prefix}/feedback",
    response_model=FeedbackResponse,
    tags=["Feedback & Trust"]
)
def submit_feedback(
    request: FeedbackRequest,
    project_id: int, # Require project_id as query param for simplicity and robustness
    db: Session = Depends(get_db)
):
    """
    Submit human feedback on any AI output.
    
    NEVER alters the original AI output.
    All feedback is audit-logged.
    """
    result = feedback_service.submit_feedback(
        db=db,
        output_id=request.output_id,
        output_type=request.output_type,
        project_id=project_id,
        feedback_type=request.feedback_type,
        comment=request.comment
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return FeedbackResponse(
        success=True,
        feedback_id=result.feedback_id,
        message=result.message,
        timestamp=result.timestamp
    )


@app.get(
    f"{settings.api_prefix}/feedback/{{output_id}}",
    response_model=FeedbackSummaryResponse,
    tags=["Feedback & Trust"]
)
def get_feedback_for_output(
    output_id: str,
    db: Session = Depends(get_db)
):
    """
    Get aggregated feedback for a specific output.
    """
    summary = feedback_service.get_feedback_for_output(db, output_id)
    
    return FeedbackSummaryResponse(
        output_id=summary.output_id,
        total_count=summary.total_count,
        helpful_count=summary.helpful_count,
        not_helpful_count=summary.not_helpful_count,
        agree_count=summary.agree_count,
        disagree_count=summary.disagree_count,
        needs_revision_count=summary.needs_revision_count,
        needs_expert_count=summary.needs_expert_count,
        disagreement_rate=summary.disagreement_rate,
        recent_comments=summary.comments
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/feedback",
    response_model=ProjectFeedbackStatsResponse,
    tags=["Feedback & Trust"]
)
def get_project_feedback(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get project-level feedback statistics.
    """
    stats = feedback_service.get_project_feedback(db, project_id)
    
    # Convert dicts to FeedbackItem objects
    recent_items = [
        FeedbackItem(
            id=item["id"],
            output_id=item["output_id"],
            output_type=item["output_type"],
            feedback_type=item["feedback_type"],
            comment=item["comment"],
            timestamp=item["timestamp"]
        )
        for item in stats.recent_feedback
    ]
    
    return ProjectFeedbackStatsResponse(
        project_id=stats.project_id,
        total_feedback=stats.total_feedback,
        total_outputs_rated=stats.total_outputs_rated,
        overall_disagreement_rate=stats.overall_disagreement_rate,
        outputs_needing_review=stats.outputs_needing_review,
        recent_feedback=recent_items
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/confidence",
    response_model=ConfidenceCalibrationResponse,
    tags=["Feedback & Trust"]
)
def get_project_confidence(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get confidence calibration state.
    
    Calculated using RULE-BASED logic (no hidden ML).
    Transparently explains why confidence is LOW/MEDIUM.
    """
    result = calibration_service.get_or_create_calibration(db, project_id)
    
    return ConfidenceCalibrationResponse(
        project_id=project_id,
        confidence_level=ConfidenceLevelResponse(result.confidence_level),
        human_review_recommended=result.human_review_recommended,
        disagreement_flag=result.disagreement_flag,
        calibration_notes=result.calibration_notes,
        metrics=result.metrics,
        badge_properties=calibration_service.get_confidence_badge(result.confidence_level),
        timestamp=datetime.utcnow().isoformat()
    )


@app.get(
    f"{settings.api_prefix}/projects/{{project_id}}/audit",
    response_model=AuditLogListResponse,
    tags=["Audit & Compliance"]
)
def get_project_audit_trail(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get audit trail for a project.
    
    Returns immutable history of actions.
    """
    logs = audit_service.get_project_audit_trail(db, project_id)
    return AuditLogListResponse(logs=logs)


@app.get(
    f"{settings.api_prefix}/system/compliance",
    response_model=ComplianceStatusResponse,
    tags=["Audit & Compliance"]
)
def get_compliance_status():
    """
    Get system compliance status.
    
    Returns Active Mode and Restricted Features.
    """
    return compliance_service.get_system_compliance_status()


# ============== System Info ==============

@app.get(f"{settings.api_prefix}/system/status", tags=["System"])
def system_status(db: Session = Depends(get_db)):
    """
    Get system status and current capabilities.
    
    Clearly communicates what is and isn't implemented.
    """
    llm_configured = bool(settings.llm_api_key and settings.llm_api_key != "your-nebius-api-key-here")
    
    # Get real counts from database
    from models import Project, CandidateEvidence
    project_count = db.query(Project).count()
    evidence_count = db.query(CandidateEvidence).count()
    paper_count = db.query(CandidateEvidence).filter(CandidateEvidence.source_type == "paper").count()
    patent_count = db.query(CandidateEvidence).filter(CandidateEvidence.source_type == "patent").count()
    
    return {
        "phase": 10,
        "version": "1.0.0",
        "ai_provider": settings.llm_provider if llm_configured else None,
        "ai_model": settings.llm_model if llm_configured else None,
        "embedding_model": settings.embedding_model,
        "real_counts": {
            "projects": project_count,
            "evidence_documents": evidence_count,
            "research_papers": paper_count,
            "patents": patent_count
        },
        "implemented": [
            "Project CRUD operations",
            "File upload and storage",
            "Data persistence (SQLite)",
            "Analysis state tracking",
            "AI: Idea clarification (assistive)",
            "AI: Text rewriting (assistive)",
            "AI: Risk explanation (assistive)",
            "Text extraction: PDF, DOCX, TXT",
            "Keyword extraction (LLM-assisted)",
            "Research paper retrieval (Semantic Scholar)",
            "Patent retrieval (USPTO)",
            "Evidence storage and auditing",
            "Embedding generation",
            "Cosine similarity computation",
            "Novelty risk classification (GREEN/YELLOW/RED/UNKNOWN)",
            "Comparative analysis: overlap/difference",
            "Evidence-grounded explanations",
            "Draft optimization: localized suggestions",
            "Suggestion acceptance/rejection tracking",
            "Venue recommendations (deterministic matching)",
            "Readiness assessment",
            "Patent claim structuring (PATENT flow only)",
            "Claim dependency graph",
            "Risk annotations linked to evidence",
            "Attorney handoff notes",
            "Human feedback capture (Persistent, never overwritten)",
            "Confidence calibration (Rule-based, never hidden)",
            "Trust control badges",
            "Immutable audit trails (Append-only)",
            "Compliance Mode (System-wide safety switch)",
            "Production hardening (Integrity checks)"
        ],
        "not_implemented": [
            "Multi-agent orchestration",
            "Legal document generation",
            "Filing cost calculation"
        ],
        "phase_10_features": {
            "audit_logs": "Full provenance for every action and output",
            "compliance_mode": "Toggle to restrict risky features (e.g. patent gen)",
            "production_ready": "Integrity checks, startup validation, hardening",
            "final_state": "System is institution-ready and defensible"
        },
        "notes": "System is FUNCTIONALLY COMPLETE. Phase 10 guarantees auditability and safety."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




