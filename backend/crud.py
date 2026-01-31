"""
CRUD Operations for Inventix AI Backend

All database operations are honest and deterministic.
No fake data, simulated progress, or AI claims.
"""
import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile

from models import Project, File, AnalysisState, ProjectType, AnalysisStatus
from schemas import ProjectCreate, ProjectUpdate
from config import get_settings

settings = get_settings()


# ============== Project CRUD ==============

def create_project(db: Session, project_data: ProjectCreate) -> Project:
    """
    Create a new project with associated analysis state.
    """
    # Create project
    db_project = Project(
        name=project_data.name,
        type=project_data.type,
        description=project_data.description,
        idea_text=project_data.idea_text,
        domain=project_data.domain
    )
    db.add(db_project)
    db.flush()  # Get the project ID
    
    # Create analysis state with honest defaults
    analysis_state = AnalysisState(
        project_id=db_project.id,
        idea_received=bool(project_data.idea_text and project_data.idea_text.strip()),
        files_uploaded=False,
        analysis_status=AnalysisStatus.NOT_STARTED,
        notes="AI analysis not implemented. Phase 1 provides data persistence only."
    )
    db.add(analysis_state)
    db.commit()
    db.refresh(db_project)
    
    return db_project


def get_project(db: Session, project_id: int) -> Optional[Project]:
    """Get a single project by ID"""
    return db.query(Project).filter(Project.id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """Get all projects with pagination"""
    return db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()


def get_projects_count(db: Session) -> int:
    """Get total count of projects"""
    return db.query(Project).count()


def update_project(db: Session, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
    """
    Update a project and recalculate analysis state.
    """
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    # Update fields that are provided
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db_project.updated_at = datetime.utcnow()
    
    # Update analysis state
    _update_analysis_state(db, db_project)
    
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int) -> bool:
    """
    Delete a project and all associated files.
    """
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    
    # Delete files from disk
    for file in db_project.files:
        if os.path.exists(file.storage_path):
            os.remove(file.storage_path)
    
    # Delete project (cascades to files and analysis_state)
    db.delete(db_project)
    db.commit()
    return True


# ============== File CRUD ==============

def save_uploaded_file(
    db: Session, 
    project_id: int, 
    upload_file: UploadFile
) -> Optional[File]:
    """
    Save an uploaded file to disk and database.
    Returns None if project doesn't exist or file type not allowed.
    """
    # Verify project exists
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    # Get file extension
    original_filename = upload_file.filename or "unknown"
    file_ext = os.path.splitext(original_filename)[1].lower()
    
    # Validate file type
    if file_ext not in settings.allowed_extensions_list:
        return None
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    storage_path = os.path.join(settings.upload_dir, unique_filename)
    
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Save file to disk
    with open(storage_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(storage_path)
    
    # Create database entry
    db_file = File(
        project_id=project_id,
        filename=unique_filename,
        original_filename=original_filename,
        file_type=file_ext,
        storage_path=storage_path,
        file_size=file_size
    )
    db.add(db_file)
    
    # Update analysis state
    _update_analysis_state(db, db_project)
    
    db.commit()
    db.refresh(db_file)
    return db_file


def get_project_files(db: Session, project_id: int) -> List[File]:
    """Get all files for a project"""
    return db.query(File).filter(File.project_id == project_id).order_by(File.uploaded_at.desc()).all()


def get_file(db: Session, file_id: int) -> Optional[File]:
    """Get a single file by ID"""
    return db.query(File).filter(File.id == file_id).first()


def delete_file(db: Session, file_id: int) -> bool:
    """
    Delete a file from disk and database.
    """
    db_file = get_file(db, file_id)
    if not db_file:
        return False
    
    project_id = db_file.project_id
    
    # Delete from disk
    if os.path.exists(db_file.storage_path):
        os.remove(db_file.storage_path)
    
    # Delete from database
    db.delete(db_file)
    
    # Update analysis state
    db_project = get_project(db, project_id)
    if db_project:
        _update_analysis_state(db, db_project)
    
    db.commit()
    return True


# ============== Analysis State ==============

def _update_analysis_state(db: Session, project: Project) -> None:
    """
    Update analysis state based on current project data.
    
    This is HONEST state tracking:
    - idea_received: True if idea_text is non-empty
    - files_uploaded: True if at least one file exists
    - analysis_status: ALWAYS NOT_STARTED (no AI in Phase 1)
    - notes: Always states that AI is not implemented
    """
    if not project.analysis_state:
        # Create if doesn't exist
        project.analysis_state = AnalysisState(project_id=project.id)
        db.add(project.analysis_state)
    
    # Count files
    file_count = db.query(File).filter(File.project_id == project.id).count()
    
    # Update state honestly
    project.analysis_state.idea_received = bool(project.idea_text and project.idea_text.strip())
    project.analysis_state.files_uploaded = file_count > 0
    project.analysis_state.analysis_status = AnalysisStatus.NOT_STARTED
    project.analysis_state.notes = "AI analysis not implemented. Phase 1 provides data persistence only."
    project.analysis_state.updated_at = datetime.utcnow()


def get_analysis_state(db: Session, project_id: int) -> Optional[AnalysisState]:
    """Get analysis state for a project"""
    return db.query(AnalysisState).filter(AnalysisState.project_id == project_id).first()
