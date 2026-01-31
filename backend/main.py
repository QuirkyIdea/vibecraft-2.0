"""
Inventix AI Backend - Phase 3
FastAPI Application Entry Point

This backend provides:
- Project CRUD operations
- File upload and storage
- Truthful analysis state tracking
- AI ASSISTANCE (not decisions!)
- Text extraction from documents
- Evidence retrieval from external sources

Phase 3 Features:
- PDF/DOCX text extraction
- LLM-based keyword extraction
- Research paper retrieval (Semantic Scholar)
- Patent retrieval (USPTO)
- Auditable evidence storage

HARD RULES:
- AI outputs are ASSISTIVE ONLY
- No novelty scores or percentages
- No legal/academic claims
- No similarity judgments
- All retrieved evidence is "candidates" only
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
from database import get_db, init_db
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
    EvidenceCandidateResponse
)
from models import AnalysisStatus, AIAction, ExtractedText, CandidateEvidence, EvidenceSource
import crud
import ai_service
import text_extraction
import retrieval_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown"""
    # Startup
    print("=" * 50)
    print("Starting Inventix AI Backend - Phase 3")
    print("=" * 50)
    init_db()
    ensure_upload_dir()
    print(f"✓ Upload directory: {settings.upload_dir}")
    print(f"✓ Database: {settings.database_url}")
    print(f"✓ CORS origins: {settings.cors_origins_list}")
    print(f"✓ LLM Provider: {settings.llm_provider}")
    print(f"✓ LLM Model: {settings.llm_model}")
    
    # Check if LLM is configured
    if not settings.llm_api_key or settings.llm_api_key == "your-nebius-api-key-here":
        print("⚠ WARNING: LLM API key not configured!")
    else:
        print("✓ LLM API key: configured")
    
    print("✓ Text Extraction: PDF, DOCX, TXT")
    print("✓ External Retrieval: Semantic Scholar, USPTO")
    print("=" * 50)
    yield
    # Shutdown
    print("Shutting down Inventix AI Backend")


app = FastAPI(
    title="Inventix AI Backend",
    description="""
    Phase 3 Backend - Evidence-Based Retrieval Layer
    
    This backend provides:
    - Honest, persistent data storage
    - AI assistance for idea clarification, text rewriting, and risk awareness
    - REAL text extraction from PDF/DOCX files
    - REAL evidence retrieval from Semantic Scholar and USPTO
    
    AI outputs are clearly labeled as ASSISTIVE ONLY.
    Retrieved documents are CANDIDATE EVIDENCE only.
    No novelty scores, no similarity judgments, no legal claims.
    """,
    version="0.3.0",
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
        "phase": 3,
        "ai_enabled": llm_configured,
        "ai_provider": settings.llm_provider if llm_configured else None,
        "text_extraction": True,
        "evidence_retrieval": True,
        "message": "Phase 3 backend operational. Text extraction and evidence retrieval available."
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
    db_project = crud.create_project(db, project)
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


# ============== System Info ==============

@app.get(f"{settings.api_prefix}/system/status", tags=["System"])
def system_status():
    """
    Get system status and current capabilities.
    
    Clearly communicates what is and isn't implemented.
    """
    llm_configured = bool(settings.llm_api_key and settings.llm_api_key != "your-nebius-api-key-here")
    
    return {
        "phase": 3,
        "version": "0.3.0",
        "ai_provider": settings.llm_provider if llm_configured else None,
        "ai_model": settings.llm_model if llm_configured else None,
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
            "Evidence storage and auditing"
        ],
        "not_implemented": [
            "Novelty scoring",
            "Similarity detection",
            "Prior art comparison",
            "Embeddings / vector search",
            "Multi-agent orchestration"
        ],
        "phase_3_limitations": [
            "Retrieved documents are CANDIDATES only",
            "No similarity scores computed",
            "No novelty claims or judgments",
            "Human review always required"
        ],
        "notes": "Phase 3 enables REAL data retrieval. Comparison is possible but NOT performed."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


