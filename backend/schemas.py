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
    ASSISTIVE_ONLY = "ASSISTIVE_ONLY"  # Phase 2: AI has provided assistance
    PENDING = "PENDING"
    BLOCKED = "BLOCKED"


class AIAction(str, Enum):
    NONE = "NONE"
    CLARIFY_IDEA = "CLARIFY_IDEA"
    REWRITE_TEXT = "REWRITE_TEXT"
    EXPLAIN_RISKS = "EXPLAIN_RISKS"


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
    """
    id: int
    project_id: int
    idea_received: bool
    files_uploaded: bool
    # Phase 3 additions
    text_extracted: bool = False
    evidence_retrieved: bool = False
    analysis_status: AnalysisStatus = AnalysisStatus.NOT_STARTED
    ai_explanations_generated: bool = False
    last_ai_action: AIAction = AIAction.NONE
    last_ai_timestamp: Optional[datetime] = None
    notes: str = "No AI analysis performed yet."
    retrieval_notes: Optional[str] = "No evidence retrieval performed yet."
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


# ============== AI Assistance Schemas ==============

class AIAssistanceRequest(BaseModel):
    """Request for AI assistance endpoints"""
    project_id: int
    text: str = Field(..., min_length=10, max_length=10000)
    context: Optional[str] = None  # e.g., "patent claim", "research abstract"


class AIAssistanceResponse(BaseModel):
    """
    Standard response for all AI assistance endpoints.
    Always includes limitations and disclaimer.
    """
    success: bool
    ai_output: str
    limitations: List[str]
    disclaimer: str
    prompt_version: str
    timestamp: str
    error: Optional[str] = None


# ============== Phase 3: Text Extraction Schemas ==============

class ExtractedTextResponse(BaseModel):
    """Response for extracted text from a file"""
    id: int
    project_id: int
    file_id: int
    extraction_method: str
    character_count: int
    extracted_at: datetime
    version: int
    # Content not included by default to avoid large responses
    
    model_config = ConfigDict(from_attributes=True)


class TextExtractionResult(BaseModel):
    """Result of text extraction operation"""
    success: bool
    project_id: int
    files_processed: int
    total_characters: int
    extraction_notes: str
    errors: List[str] = []


# ============== Phase 3: Keyword Extraction Schemas ==============

class KeywordExtractionRequest(BaseModel):
    """Request for keyword extraction"""
    project_id: int
    text: Optional[str] = None  # If not provided, uses extracted text


class KeywordExtractionResponse(BaseModel):
    """Response from LLM-based keyword extraction"""
    success: bool
    keywords: List[str]
    concepts: List[str]
    technical_phrases: List[str]
    notes: str = "Keywords extracted using LLM. This is assistive only."
    error: Optional[str] = None


# ============== Phase 3: Evidence Retrieval Schemas ==============

class EvidenceSource(str, Enum):
    SEMANTIC_SCHOLAR = "SEMANTIC_SCHOLAR"
    USPTO = "USPTO"
    ARXIV = "ARXIV"


class EvidenceCandidateResponse(BaseModel):
    """Single candidate evidence item"""
    id: int
    title: str
    authors: str
    abstract: Optional[str]
    source_name: str
    source_url: str  # MUST be verifiable
    publication_date: Optional[str]
    retrieved_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RetrievalRequest(BaseModel):
    """Request for external retrieval"""
    project_id: int
    keywords: Optional[List[str]] = None  # If not provided, extracts from project
    limit: int = Field(default=10, ge=1, le=50)


class RetrievalResponse(BaseModel):
    """Response from external retrieval"""
    success: bool
    source: str  # "Semantic Scholar", "USPTO"
    candidates_stored: int
    search_query: str
    retrieval_notes: str  # Explains this is just evidence, no similarity scores
    error: Optional[str] = None


class ProjectEvidenceResponse(BaseModel):
    """All candidate evidence for a project"""
    project_id: int
    papers: List[EvidenceCandidateResponse]
    patents: List[EvidenceCandidateResponse]
    total_evidence: int
    notes: str = "These are candidate documents only. No similarity scores or judgments."


