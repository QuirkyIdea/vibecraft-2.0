"""
Pydantic Schemas for API Request/Response validation

These schemas define the API contract between frontend and backend.
All responses are honest - no fake data or simulated progress.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============== Enums ==============

class ProjectType(str, Enum):
    RESEARCH = "RESEARCH"
    PATENT = "PATENT"
    MIXED = "MIXED"


class AnalysisStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"


# ============== File Schemas ==============

class FileBase(BaseModel):
    """Base file schema"""
    original_filename: str
    file_type: str
    file_size: int


class FileCreate(FileBase):
    """Schema for file creation (internal use)"""
    filename: str
    storage_path: str


class FileResponse(FileBase):
    """File response returned to frontend"""
    id: int
    project_id: int
    filename: str
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== AnalysisState Schemas ==============

class AnalysisStateResponse(BaseModel):
    """
    Analysis state response - always honest about current capabilities.
    
    Phase 1:
    - analysis_status is always NOT_STARTED
    - notes clearly state AI is not implemented
    """
    id: int
    project_id: int
    idea_received: bool
    files_uploaded: bool
    analysis_status: AnalysisStatus = AnalysisStatus.NOT_STARTED
    notes: str = "AI analysis not implemented. Phase 1 provides data persistence only."
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== Project Schemas ==============

class ProjectBase(BaseModel):
    """Base project fields"""
    name: str = Field(..., min_length=1, max_length=255)
    type: ProjectType = ProjectType.RESEARCH
    description: Optional[str] = None
    idea_text: Optional[str] = None
    domain: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[ProjectType] = None
    description: Optional[str] = None
    idea_text: Optional[str] = None
    domain: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response without nested relations"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with files and analysis state"""
    files: List[FileResponse] = []
    analysis_state: Optional[AnalysisStateResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============== List Response ==============

class ProjectListResponse(BaseModel):
    """Response for listing projects"""
    projects: List[ProjectResponse]
    total: int


# ============== API Response Wrappers ==============

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
