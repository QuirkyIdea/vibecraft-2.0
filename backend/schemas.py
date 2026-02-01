"""
Pydantic Schemas for API Request/Response validation

These schemas define the API contract between frontend and backend.
All responses are honest - no fake data or simulated progress.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
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


class NoveltyRiskLevel(str, Enum):
    GREEN = "GREEN"      # Low overlap - likely novel
    YELLOW = "YELLOW"    # Partial overlap - needs review
    RED = "RED"          # High overlap - significant concern
    UNKNOWN = "UNKNOWN"  # Insufficient evidence


class DraftMode(str, Enum):
    PATENT = "patent"
    RESEARCH = "research"


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
    # Phase 4 additions
    similarity_computed: bool = False
    novelty_risk: NoveltyRiskLevel = NoveltyRiskLevel.UNKNOWN
    max_similarity_score: Optional[float] = None
    top_evidence_id: Optional[int] = None
    # Phase 5 additions
    comparison_generated: bool = False
    comparison_version: Optional[int] = None
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


# ============== Drafting Schemas ==============

class DraftingRequest(BaseModel):
    """Request for draft generation via draft_patentai"""
    project_id: int
    document_id: Optional[str] = None
    text: Optional[str] = None
    mode: DraftMode = DraftMode.PATENT


class DraftSectionResponse(BaseModel):
    heading: str
    content: str


class DraftingResponse(BaseModel):
    success: bool
    project_id: int
    document_id: str
    mode: DraftMode
    output: Optional[str] = None
    sections: List[DraftSectionResponse] = []
    error: Optional[str] = None


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


# ============== Phase 4: Similarity & Novelty Schemas ==============

class SimilarityMatch(BaseModel):
    """Single similarity match with evidence"""
    evidence_id: int
    title: str
    authors: str
    source: str
    source_url: str  # Verifiable URL
    evidence_type: str  # "paper" or "patent"
    similarity_score: float  # 0.0 - 1.0
    
    model_config = ConfigDict(from_attributes=True)


class EmbeddingGenerationResponse(BaseModel):
    """Response from embedding generation"""
    success: bool
    project_id: int
    idea_embedded: bool
    evidence_embedded: int
    total_evidence: int
    notes: str
    error: Optional[str] = None


class SimilarityComputationResponse(BaseModel):
    """Response from similarity computation"""
    success: bool
    project_id: int
    scores_computed: int
    max_score: Optional[float]
    notes: str
    error: Optional[str] = None


class NoveltyRiskResponse(BaseModel):
    """
    Complete novelty risk assessment with evidence attribution.
    
    EVERY risk is traceable to specific evidence.
    """
    project_id: int
    novelty_risk: NoveltyRiskLevel
    max_similarity_score: Optional[float]
    top_match: Optional[SimilarityMatch]
    research_risk: NoveltyRiskLevel
    research_max_score: Optional[float]
    research_matches: int
    patent_risk: NoveltyRiskLevel
    patent_max_score: Optional[float]
    patent_matches: int
    total_evidence_compared: int
    explanation: Optional[str] = None
    notes: str


class SimilarityDetailRequest(BaseModel):
    """Request for similarity details"""
    project_id: int
    evidence_type: Optional[str] = None  # "paper" or "patent" or None for all
    limit: int = Field(default=10, ge=1, le=50)
    explain: bool = False  # Whether to include LLM explanation


class SimilarityListResponse(BaseModel):
    """List of all similarity scores for a project"""
    project_id: int
    matches: List[SimilarityMatch]
    total: int
    notes: str = "Similarity based on semantic comparison. Higher score = more overlap."


# ============== Phase 5: Comparative Analysis Schemas ==============

class OverlapPoint(BaseModel):
    """Single overlap between idea and evidence"""
    idea_concept: str
    evidence_concept: str
    evidence_id: Optional[int] = None
    evidence_title: Optional[str] = None


class DifferencePoint(BaseModel):
    """Single difference with required uncertainty"""
    aspect: str
    description: str
    uncertainty: str  # Required uncertainty language


class EvidenceSummaryItem(BaseModel):
    """Summary of one evidence document"""
    evidence_id: int
    title: str
    source: str
    source_url: str
    similarity_score: float
    summary: str


class ComparativeAnalysisRequest(BaseModel):
    """Request for comparative analysis"""
    project_id: int
    top_k: int = Field(default=5, ge=1, le=10)  # Number of evidence to compare


class ComparativeAnalysisResponse(BaseModel):
    """Complete comparative analysis with evidence grounding"""
    project_id: int
    version: int
    novelty_risk: NoveltyRiskLevel
    max_similarity: Optional[float]
    
    # Evidence summaries
    evidence_summaries: List[EvidenceSummaryItem]
    
    # Analysis sections
    existing_landscape: str
    overlap_points: List[OverlapPoint]
    difference_points: List[DifferencePoint]
    novelty_explanation: str
    
    # Limitations (always present)
    limitations: List[str]
    confidence_level: str  # "low", "medium", "high"
    recommendation: str
    
    # Metadata
    evidence_count: int
    research_count: int
    patent_count: int
    generated_at: str


class ComparativeAnalysisSummary(BaseModel):
    """Summary of comparative analysis for project listing"""
    project_id: int
    version: int
    novelty_risk: NoveltyRiskLevel
    confidence_level: str
    evidence_count: int
    generated_at: str
    has_overlaps: bool
    has_differences: bool


# ============== Phase 6: Draft Optimization Schemas ==============

class SuggestionStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ChangeType(str, Enum):
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    OVERLAP_REDUCTION = "overlap_reduction"
    STRUCTURE = "structure"


class PreservesIntent(str, Enum):
    YES = "YES"
    POSSIBLY = "POSSIBLY"
    NO = "NO"


class DraftOptimizeRequest(BaseModel):
    """Request for draft optimization"""
    draft_text: str = Field(..., min_length=50, max_length=50000)


class DraftSuggestionItem(BaseModel):
    """Single draft suggestion"""
    id: Optional[int] = None
    original_text_snippet: str
    suggested_revision: str
    reason_for_change: str
    change_type: ChangeType
    preserves_intent: PreservesIntent
    status: SuggestionStatus = SuggestionStatus.PENDING
    start_position: Optional[int] = None
    end_position: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DraftOptimizeResponse(BaseModel):
    """Response from draft optimization"""
    success: bool
    project_id: int
    draft_version_id: int
    version: int
    suggestions: List[DraftSuggestionItem]
    total_suggestions: int
    limitations: List[str]
    disclaimer: str
    error: Optional[str] = None


class SuggestionUpdateRequest(BaseModel):
    """Request to update suggestion status"""
    status: SuggestionStatus


class SuggestionUpdateResponse(BaseModel):
    """Response from suggestion update"""
    success: bool
    suggestion_id: int
    new_status: SuggestionStatus
    message: str


class DraftVersionResponse(BaseModel):
    """Response for a draft version"""
    id: int
    project_id: int
    version: int
    original_text: str
    suggestions_count: int
    pending_count: int
    accepted_count: int
    rejected_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DraftHistoryResponse(BaseModel):
    """Response for draft version history"""
    project_id: int
    versions: List[DraftVersionResponse]
    total: int


# ============== Phase 7: Venue Recommendation Schemas ==============

class VenueType(str, Enum):
    CONFERENCE = "CONFERENCE"
    JOURNAL = "JOURNAL"
    WORKSHOP = "WORKSHOP"


class ReadinessLevel(str, Enum):
    WORKSHOP = "WORKSHOP"
    CONFERENCE = "CONFERENCE"
    JOURNAL = "JOURNAL"
    REFINE = "REFINE"


class VenueRecommendationItem(BaseModel):
    """Single venue recommendation."""
    name: str
    short_name: str
    venue_type: VenueType
    domains: List[str]
    relevance_reason: str
    submission_formats: List[str]
    match_strength: str  # "strong", "moderate", "weak"
    cautions: List[str]


class ReadinessNotesResponse(BaseModel):
    """Readiness assessment for submission."""
    level: ReadinessLevel
    explanation: str
    suggestions: List[str]


class VenueRecommendationRequest(BaseModel):
    """Request for venue recommendations."""
    project_id: int


class VenueRecommendationResponse(BaseModel):
    """Complete venue recommendation response."""
    success: bool
    project_id: int
    venues: List[VenueRecommendationItem]
    readiness: ReadinessNotesResponse
    general_guidance: List[str]
    limitations: List[str]
    disclaimer: str
    keyword_count: int
    evidence_count: int
    novelty_risk: NoveltyRiskLevel
    error: Optional[str] = None


# ============== Phase 8: Patent Claim Structuring Schemas ==============

class ClaimType(str, Enum):
    INDEPENDENT = "INDEPENDENT"
    DEPENDENT = "DEPENDENT"


class ClaimRiskType(str, Enum):
    BROAD = "BROAD"
    OVERLAP = "OVERLAP"
    NEEDS_NARROWING = "NEEDS_NARROWING"


class ClaimFlagType(str, Enum):
    UNCLEAR = "UNCLEAR"
    INCORRECT = "INCORRECT"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ClaimDraftItem(BaseModel):
    """Single claim draft item."""
    id: Optional[int] = None
    claim_number: int
    claim_type: ClaimType
    claim_text: str
    technical_feature: str
    explanation: str
    parent_claim_number: Optional[int] = None
    is_flagged: bool = False
    flag_type: Optional[ClaimFlagType] = None
    flag_notes: Optional[str] = None


class ClaimRiskAnnotationItem(BaseModel):
    """Risk annotation for a claim."""
    id: Optional[int] = None
    claim_number: int
    risk_type: ClaimRiskType
    description: str
    evidence_id: Optional[int] = None
    evidence_title: Optional[str] = None


class ClaimDependencyEdge(BaseModel):
    """Edge in dependency graph."""
    from_claim: int
    to_claim: int
    label: str = "depends on"


class ClaimDependencyGraph(BaseModel):
    """Visualization-ready dependency graph."""
    nodes: List[Dict[str, Any]]
    edges: List[ClaimDependencyEdge]
    root_claims: List[int]


class AttorneyHandoffNotes(BaseModel):
    """Notes for attorney handoff."""
    independent_claims: int
    dependent_claims: int
    review_areas: List[str]
    prior_art_notes: str
    novelty_risk: str
    risk_recommendation: str
    raw_text: str


class ClaimGenerationRequest(BaseModel):
    """Request to generate claim structure."""
    # No body needed - uses project data
    pass


class ClaimGenerationResponse(BaseModel):
    """Complete claim generation response."""
    success: bool
    project_id: int
    claims: List[ClaimDraftItem]
    risks: List[ClaimRiskAnnotationItem]
    dependency_graph: ClaimDependencyGraph
    attorney_handoff: AttorneyHandoffNotes
    disclaimer: str
    version: int
    generation_id: int
    error: Optional[str] = None


class ClaimUpdateRequest(BaseModel):
    """Request to update a claim."""
    claim_text: str
    technical_feature: Optional[str] = None
    explanation: Optional[str] = None


class ClaimUpdateResponse(BaseModel):
    """Response after updating a claim."""
    success: bool
    claim_id: int
    new_version: int
    message: str


class ClaimFlagRequest(BaseModel):
    """Request to flag a claim."""
    flag_type: ClaimFlagType
    notes: Optional[str] = None


class ClaimFlagResponse(BaseModel):
    """Response after flagging a claim."""
    success: bool
    claim_id: int
    message: str


class ClaimsListResponse(BaseModel):
    """Response listing all claims for a project."""
    project_id: int
    claims: List[ClaimDraftItem]
    risks: List[ClaimRiskAnnotationItem]
    total_claims: int
    disclaimer: str


# ============== Phase 9: Feedback & Calibration Schemas ==============

class FeedbackTypeResponse(str, Enum):
    """Feedback type enum for responses."""
    HELPFUL = "HELPFUL"
    NOT_HELPFUL = "NOT_HELPFUL"
    AGREE = "AGREE"
    DISAGREE = "DISAGREE"
    NEEDS_REVISION = "NEEDS_REVISION"
    NEEDS_EXPERT = "NEEDS_EXPERT"


class ConfidenceLevelResponse(str, Enum):
    """Confidence level enum for responses."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FeedbackRequest(BaseModel):
    """Request to submit feedback."""
    output_id: str
    output_type: str
    feedback_type: str
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response after submitting feedback."""
    success: bool
    feedback_id: int
    message: str
    timestamp: str


class FeedbackItem(BaseModel):
    """Single feedback item."""
    id: int
    output_id: str
    output_type: str
    feedback_type: str
    comment: Optional[str]
    timestamp: str


class FeedbackSummaryResponse(BaseModel):
    """Aggregated feedback summary for an output."""
    output_id: str
    total_count: int
    helpful_count: int
    not_helpful_count: int
    agree_count: int
    disagree_count: int
    needs_revision_count: int
    needs_expert_count: int
    disagreement_rate: float
    recent_comments: List[str]


class ProjectFeedbackStatsResponse(BaseModel):
    """Project-level feedback statistics."""
    project_id: int
    total_feedback: int
    total_outputs_rated: int
    overall_disagreement_rate: float
    outputs_needing_review: int
    recent_feedback: List[FeedbackItem]


class ConfidenceCalibrationResponse(BaseModel):
    """Confidence calibration state."""
    project_id: int
    confidence_level: ConfidenceLevelResponse
    human_review_recommended: bool
    disagreement_flag: bool
    calibration_notes: List[str]
    metrics: Dict[str, Any]
    badge_properties: Dict[str, str]
    timestamp: str


# ============== Phase 10: Audit & Compliance Schemas ==============

class AuditLogItem(BaseModel):
    """Single audit log entry."""
    id: int
    action_type: str
    entity_type: str
    entity_id: Optional[int]
    user_id: Optional[str]
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AuditLogListResponse(BaseModel):
    """List of audit logs."""
    logs: List[AuditLogItem]

class ComplianceStatusResponse(BaseModel):
    """System compliance status."""
    compliance_mode_active: bool
    restricted_features: List[str]
    audit_logging_enabled: bool


