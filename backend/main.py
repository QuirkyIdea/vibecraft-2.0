"""
Inventix AI Backend - Phase 1
FastAPI Application Entry Point

This is a MINIMAL, HONEST backend that provides:
- Project CRUD operations
- File upload and storage
- Truthful analysis state tracking

What this does NOT do (Phase 1 limitations):
- No AI/LLM integration
- No novelty scoring or similarity detection
- No patent analysis
- No multi-agent orchestration
- No fake progress or percentages

All responses clearly communicate current limitations.
"""
from contextlib import asynccontextmanager
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
    ErrorResponse
)
import crud

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown"""
    # Startup
    print("=" * 50)
    print("Starting Inventix AI Backend - Phase 1")
    print("=" * 50)
    init_db()
    ensure_upload_dir()
    print(f"✓ Upload directory: {settings.upload_dir}")
    print(f"✓ Database: {settings.database_url}")
    print(f"✓ CORS origins: {settings.cors_origins_list}")
    print("=" * 50)
    yield
    # Shutdown
    print("Shutting down Inventix AI Backend")


app = FastAPI(
    title="Inventix AI Backend",
    description="""
    Phase 1 Backend - Minimal Real Foundation
    
    This backend provides honest, persistent data storage.
    No AI features are implemented in this phase.
    
    All analysis states will show:
    - status: NOT_STARTED
    - notes: "AI analysis not implemented"
    """,
    version="0.1.0",
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
    return {
        "status": "healthy",
        "phase": 1,
        "ai_enabled": False,
        "message": "Phase 1 backend operational. AI features not implemented."
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
    Analysis state will always show:
    - analysis_status: NOT_STARTED
    - notes: "AI analysis not implemented"
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
    
    Note: Files are stored but NOT processed.
    No text extraction, embedding, or analysis in Phase 1.
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


# ============== System Info ==============

@app.get(f"{settings.api_prefix}/system/status", tags=["System"])
def system_status():
    """
    Get system status and Phase 1 limitations.
    
    This endpoint clearly communicates what is and isn't implemented.
    """
    return {
        "phase": 1,
        "version": "0.1.0",
        "implemented": [
            "Project CRUD operations",
            "File upload and storage",
            "Data persistence (SQLite)",
            "Analysis state tracking (honest)"
        ],
        "not_implemented": [
            "AI/LLM integration",
            "Text extraction from documents",
            "Novelty scoring",
            "Similarity detection",
            "Patent analysis",
            "Research synthesis",
            "Multi-agent orchestration",
            "Knowledge graph generation"
        ],
        "notes": "All AI features will show status=NOT_STARTED. This is intentional and honest."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
