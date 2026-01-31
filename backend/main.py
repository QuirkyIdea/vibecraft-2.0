"""
Inventix AI Backend - Phase 2
FastAPI Application Entry Point

This backend provides:
- Project CRUD operations
- File upload and storage
- Truthful analysis state tracking
- AI ASSISTANCE (not decisions!)

AI Features (Phase 2):
- Idea clarification
- Text rewriting
- Risk explanation

HARD RULES:
- AI outputs are ASSISTIVE ONLY
- No novelty scores or percentages
- No legal/academic claims
- All outputs include disclaimers
"""
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List
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
    AIAssistanceResponse
)
from models import AnalysisStatus, AIAction
import crud
import ai_service

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown"""
    # Startup
    print("=" * 50)
    print("Starting Inventix AI Backend - Phase 2")
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
    
    print("=" * 50)
    yield
    # Shutdown
    print("Shutting down Inventix AI Backend")


app = FastAPI(
    title="Inventix AI Backend",
    description="""
    Phase 2 Backend - AI Assistance Layer
    
    This backend provides:
    - Honest, persistent data storage
    - AI assistance for idea clarification, text rewriting, and risk awareness
    
    AI outputs are clearly labeled as ASSISTIVE ONLY.
    No novelty scores, no legal claims, no certainty.
    """,
    version="0.2.0",
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
        "phase": 2,
        "ai_enabled": llm_configured,
        "ai_provider": settings.llm_provider if llm_configured else None,
        "message": "Phase 2 backend operational. AI assistance available." if llm_configured else "Phase 2 backend operational. LLM not configured."
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
    
    Note: Files are stored but NOT processed by AI.
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
        "phase": 2,
        "version": "0.2.0",
        "ai_provider": settings.llm_provider if llm_configured else None,
        "ai_model": settings.llm_model if llm_configured else None,
        "implemented": [
            "Project CRUD operations",
            "File upload and storage",
            "Data persistence (SQLite)",
            "Analysis state tracking",
            "AI: Idea clarification (assistive)",
            "AI: Text rewriting (assistive)",
            "AI: Risk explanation (assistive)"
        ],
        "not_implemented": [
            "Novelty scoring",
            "Similarity detection",
            "Prior art search",
            "Patent analysis",
            "Research synthesis",
            "Multi-agent orchestration",
            "Document text extraction"
        ],
        "ai_limitations": [
            "AI outputs are ASSISTIVE ONLY",
            "No novelty claims or scores",
            "No legal or academic authority",
            "Human review always required"
        ],
        "notes": "AI features provide assistance only. Never automated decisions."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

