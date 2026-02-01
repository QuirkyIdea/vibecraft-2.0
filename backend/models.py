"""
SQLAlchemy ORM Models for Inventix AI

Models:
- Project: Core project entity
- File: Uploaded files associated with projects
- AnalysisState: Tracks project analysis status (honest state)
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base


class AnalysisStatus(str, PyEnum):
    """Analysis status enum"""
    NOT_STARTED = "NOT_STARTED"
    ASSISTIVE_ONLY = "ASSISTIVE_ONLY"  # Phase 2: AI has provided assistance
    PENDING = "PENDING"  # Reserved for future phases
    BLOCKED = "BLOCKED"  # Reserved for future phases


class AIAction(str, PyEnum):
    """Types of AI actions performed"""
    NONE = "NONE"
    CLARIFY_IDEA = "CLARIFY_IDEA"
    REWRITE_TEXT = "REWRITE_TEXT"
    EXPLAIN_RISKS = "EXPLAIN_RISKS"


class ProjectType(str, PyEnum):
    """Project type enum"""
    RESEARCH = "RESEARCH"
    PATENT = "PATENT"
    MIXED = "MIXED"


class Project(Base):
    """
    Project model - the core entity for user projects.
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(ProjectType), default=ProjectType.RESEARCH, nullable=False)
    description = Column(Text, nullable=True)
    idea_text = Column(Text, nullable=True)  # User's idea/problem statement
    domain = Column(String(100), nullable=True)  # e.g., "AI", "BIOTECH"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")
    analysis_state = relationship("AnalysisState", back_populates="project", uselist=False, cascade="all, delete-orphan")
    extracted_texts = relationship("ExtractedText", back_populates="project", cascade="all, delete-orphan")
    candidate_evidence = relationship("CandidateEvidence", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', type={self.type})>"


class File(Base):
    """
    File model - tracks uploaded files.
    Files are stored on disk, metadata in database.
    """
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)  # Stored filename (UUID-based)
    original_filename = Column(String(255), nullable=False)  # User's original filename
    file_type = Column(String(50), nullable=False)  # e.g., ".pdf", ".docx"
    storage_path = Column(String(500), nullable=False)  # Full path on disk
    file_size = Column(Integer, nullable=False)  # Size in bytes
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="files")
    extracted_text = relationship("ExtractedText", back_populates="file", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<File(id={self.id}, original_filename='{self.original_filename}')>"


class ExtractedText(Base):
    """
    ExtractedText model - stores REAL text extracted from files.
    
    Phase 3: No hallucination - only actual document content.
    """
    __tablename__ = "extracted_texts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    extraction_method = Column(String(50), nullable=False)  # "pdf", "docx", "text"
    character_count = Column(Integer, nullable=False)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="extracted_texts")
    file = relationship("File", back_populates="extracted_text")
    
    def __repr__(self):
        return f"<ExtractedText(file_id={self.file_id}, chars={self.character_count})>"


class EvidenceSource(str, PyEnum):
    """Source of candidate evidence"""
    SEMANTIC_SCHOLAR = "SEMANTIC_SCHOLAR"
    USPTO = "USPTO"
    ARXIV = "ARXIV"


class CandidateEvidence(Base):
    """
    CandidateEvidence model - stores REAL external documents.
    
    Phase 3: No similarity scores, no judgments - just evidence candidates.
    Every item MUST have a verifiable source URL.
    """
    __tablename__ = "candidate_evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    source_type = Column(String(50), nullable=False)  # "paper" or "patent"
    title = Column(String(500), nullable=False)
    authors = Column(String(500), nullable=False)
    abstract = Column(Text, nullable=True)
    source_name = Column(Enum(EvidenceSource), nullable=False)
    source_url = Column(String(500), nullable=False)  # MUST be verifiable
    publication_date = Column(String(50), nullable=True)
    search_query = Column(String(500), nullable=False)  # What keywords were used
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="candidate_evidence")
    
    def __repr__(self):
        return f"<CandidateEvidence(id={self.id}, title='{self.title[:30]}...')>"


class NoveltyRiskLevel(str, PyEnum):
    """Novelty risk classification"""
    GREEN = "GREEN"      # Low overlap - likely novel
    YELLOW = "YELLOW"    # Partial overlap - needs review
    RED = "RED"          # High overlap - significant concern
    UNKNOWN = "UNKNOWN"  # Insufficient evidence


class IdeaEmbedding(Base):
    """
    IdeaEmbedding model - stores embedding vector for user's idea.
    
    Phase 4: Used for semantic similarity computation.
    """
    __tablename__ = "idea_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)
    embedding = Column(Text, nullable=False)  # JSON array of floats
    text_hash = Column(String(64), nullable=False)  # For cache invalidation
    model_name = Column(String(100), nullable=False)
    dimensions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", backref="idea_embedding")
    
    def __repr__(self):
        return f"<IdeaEmbedding(project_id={self.project_id}, dims={self.dimensions})>"


class EvidenceEmbedding(Base):
    """
    EvidenceEmbedding model - stores embedding for candidate evidence.
    
    Phase 4: Cached for efficient similarity computation.
    """
    __tablename__ = "evidence_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(Integer, ForeignKey("candidate_evidence.id"), unique=True, nullable=False)
    embedding = Column(Text, nullable=False)  # JSON array of floats
    text_hash = Column(String(64), nullable=False)
    model_name = Column(String(100), nullable=False)
    dimensions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    evidence = relationship("CandidateEvidence", backref="embedding")
    
    def __repr__(self):
        return f"<EvidenceEmbedding(evidence_id={self.evidence_id})>"


class SimilarityScore(Base):
    """
    SimilarityScore model - stores computed similarity between idea and evidence.
    
    Phase 4: Every score links to specific evidence (no orphan scores).
    """
    __tablename__ = "similarity_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    evidence_id = Column(Integer, ForeignKey("candidate_evidence.id"), nullable=False)
    score = Column(Integer, nullable=False)  # Stored as int (score * 10000 for precision)
    evidence_type = Column(String(20), nullable=False)  # "paper" or "patent"
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", backref="similarity_scores")
    evidence = relationship("CandidateEvidence", backref="similarity_score")
    
    @property
    def score_float(self) -> float:
        """Get score as float (0.0 - 1.0)"""
        return self.score / 10000.0
    
    def __repr__(self):
        return f"<SimilarityScore(project={self.project_id}, evidence={self.evidence_id}, score={self.score_float:.4f})>"


class AnalysisState(Base):
    """
    AnalysisState model - tracks honest state of project analysis.
    
    Phase 4 additions:
    - similarity_computed: True when similarity computed
    - novelty_risk: GREEN/YELLOW/RED/UNKNOWN
    - max_similarity_score: Top similarity score
    - top_evidence_id: ID of most similar evidence
    """
    __tablename__ = "analysis_states"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)
    
    # State flags (automatically computed)
    idea_received = Column(Boolean, default=False, nullable=False)
    files_uploaded = Column(Boolean, default=False, nullable=False)
    
    # Phase 3: Text extraction and retrieval flags
    text_extracted = Column(Boolean, default=False, nullable=False)
    evidence_retrieved = Column(Boolean, default=False, nullable=False)
    
    # Phase 4: Similarity and novelty flags
    similarity_computed = Column(Boolean, default=False, nullable=False)
    novelty_risk = Column(
        Enum(NoveltyRiskLevel),
        default=NoveltyRiskLevel.UNKNOWN,
        nullable=False
    )
    max_similarity_score = Column(Integer, nullable=True)  # Score * 10000
    top_evidence_id = Column(Integer, nullable=True)
    
    # Analysis status
    analysis_status = Column(
        Enum(AnalysisStatus), 
        default=AnalysisStatus.NOT_STARTED, 
        nullable=False
    )
    
    # AI assistance tracking (Phase 2)
    ai_explanations_generated = Column(Boolean, default=False, nullable=False)
    last_ai_action = Column(Enum(AIAction), default=AIAction.NONE, nullable=False)
    last_ai_timestamp = Column(DateTime, nullable=True)
    
    # Honest notes about current state
    notes = Column(
        Text, 
        default="No AI analysis performed yet.",
        nullable=False
    )
    
    # Phase 3: Retrieval-specific notes
    retrieval_notes = Column(
        Text,
        default="No evidence retrieval performed yet.",
        nullable=True
    )
    
    # Phase 5: Comparative analysis flags
    comparison_generated = Column(Boolean, default=False, nullable=False)
    comparison_version = Column(Integer, nullable=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="analysis_state")
    
    @property
    def max_similarity_float(self) -> float:
        """Get max similarity as float (0.0 - 1.0)"""
        if self.max_similarity_score is None:
            return None
        return self.max_similarity_score / 10000.0
    
    def __repr__(self):
        return f"<AnalysisState(project_id={self.project_id}, risk={self.novelty_risk})>"


class ComparativeAnalysis(Base):
    """
    ComparativeAnalysis model - stores evidence-grounded comparative summaries.
    
    Phase 5: Explains novelty with traceable claims.
    """
    __tablename__ = "comparative_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    
    # Evidence used (JSON array of IDs)
    evidence_ids = Column(Text, nullable=False)
    
    # Structured analysis (JSON)
    existing_work_summary = Column(Text, nullable=True)
    overlap_analysis = Column(Text, nullable=True)  # JSON array
    differentiation_analysis = Column(Text, nullable=True)  # JSON array
    novelty_explanation = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)  # JSON array
    confidence_level = Column(String(20), nullable=True)  # low/medium/high
    
    # Metadata
    input_novelty_risk = Column(String(20), nullable=False)  # Risk at time of generation
    input_max_similarity = Column(Integer, nullable=True)  # Score at time of generation
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", backref="comparative_analyses")
    
    def __repr__(self):
        return f"<ComparativeAnalysis(project={self.project_id}, v={self.version})>"


# ============== Phase 6: Draft Optimization Models ==============

class SuggestionStatus(str, PyEnum):
    """Status of a draft suggestion"""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ChangeType(str, PyEnum):
    """Type of suggested change"""
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    OVERLAP_REDUCTION = "overlap_reduction"
    STRUCTURE = "structure"


class PreservesIntent(str, PyEnum):
    """Whether suggestion preserves author's intent"""
    YES = "YES"
    POSSIBLY = "POSSIBLY"
    NO = "NO"


class DraftVersion(Base):
    """
    DraftVersion model - stores user's draft text for optimization.
    
    Phase 6: Tracks original text and version history.
    """
    __tablename__ = "draft_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version = Column(Integer, default=1, nullable=False)
    original_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", backref="draft_versions")
    suggestions = relationship("DraftSuggestion", back_populates="draft_version", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DraftVersion(project={self.project_id}, v={self.version})>"


class DraftSuggestion(Base):
    """
    DraftSuggestion model - stores individual optimization suggestions.
    
    Phase 6: Each suggestion is localized, explainable, and rejectable.
    """
    __tablename__ = "draft_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    draft_version_id = Column(Integer, ForeignKey("draft_versions.id"), nullable=False)
    
    # The original text snippet being suggested for change
    original_snippet = Column(Text, nullable=False)
    
    # The suggested revision
    suggested_revision = Column(Text, nullable=False)
    
    # Explanation for why this change is suggested
    reason = Column(Text, nullable=False)
    
    # Type of change
    change_type = Column(Enum(ChangeType), nullable=False)
    
    # Whether this preserves the author's intent
    preserves_intent = Column(Enum(PreservesIntent), nullable=False)
    
    # User's decision
    status = Column(Enum(SuggestionStatus), default=SuggestionStatus.PENDING, nullable=False)
    
    # Position in original text (for UI highlighting)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    draft_version = relationship("DraftVersion", back_populates="suggestions")
    
    def __repr__(self):
        return f"<DraftSuggestion(id={self.id}, type={self.change_type}, status={self.status})>"


# ============== Phase 8: Patent Claim Structuring Models ==============

class ClaimType(str, PyEnum):
    """Type of patent claim"""
    INDEPENDENT = "INDEPENDENT"
    DEPENDENT = "DEPENDENT"


class ClaimRiskType(str, PyEnum):
    """Risk type for claim annotations"""
    BROAD = "BROAD"  # Claim may be too broad
    OVERLAP = "OVERLAP"  # Overlaps with prior art
    NEEDS_NARROWING = "NEEDS_NARROWING"  # Should be narrowed


class ClaimFlagType(str, PyEnum):
    """User-flagged concern types"""
    UNCLEAR = "UNCLEAR"
    INCORRECT = "INCORRECT"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ClaimDraft(Base):
    """
    ClaimDraft model - stores patent claim drafts.
    
    Phase 8: CONCEPTUAL DRAFTS ONLY - NOT LEGAL ADVICE.
    Versioned and immutable once finalized.
    """
    __tablename__ = "claim_drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Claim structure
    version = Column(Integer, default=1, nullable=False)
    claim_number = Column(Integer, nullable=False)  # 1, 2, 3...
    claim_type = Column(Enum(ClaimType), nullable=False)
    
    # Claim content
    claim_text = Column(Text, nullable=False)
    technical_feature = Column(Text, nullable=True)  # What feature this covers
    explanation = Column(Text, nullable=True)  # Why structured this way
    
    # Dependency (for dependent claims)
    parent_claim_id = Column(Integer, ForeignKey("claim_drafts.id"), nullable=True)
    
    # State
    is_immutable = Column(Boolean, default=False, nullable=False)
    user_edited = Column(Boolean, default=False, nullable=False)
    
    # User flags
    is_flagged = Column(Boolean, default=False, nullable=False)
    flag_type = Column(Enum(ClaimFlagType), nullable=True)
    flag_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", backref="claim_drafts")
    parent_claim = relationship("ClaimDraft", remote_side=[id], backref="dependent_claims")
    risk_annotations = relationship("ClaimRiskAnnotation", back_populates="claim", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ClaimDraft(id={self.id}, num={self.claim_number}, type={self.claim_type})>"


class ClaimRiskAnnotation(Base):
    """
    ClaimRiskAnnotation model - stores risk annotations for claims.
    
    Phase 8: Links risks to prior art evidence when applicable.
    """
    __tablename__ = "claim_risk_annotations"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claim_drafts.id"), nullable=False)
    
    # Risk info
    risk_type = Column(Enum(ClaimRiskType), nullable=False)
    description = Column(Text, nullable=False)
    
    # Link to evidence (optional - for OVERLAP risks)
    evidence_id = Column(Integer, ForeignKey("candidate_evidence.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    claim = relationship("ClaimDraft", back_populates="risk_annotations")
    evidence = relationship("CandidateEvidence", backref="risk_annotations")
    
    def __repr__(self):
        return f"<ClaimRiskAnnotation(claim={self.claim_id}, type={self.risk_type})>"


class ClaimGenerationMetadata(Base):
    """
    ClaimGenerationMetadata - tracks claim generation for auditing.
    
    Phase 8: Records model, prompt version, and input hash.
    """
    __tablename__ = "claim_generation_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Generation info
    model_used = Column(String(100), nullable=False)
    prompt_version = Column(String(20), nullable=False)
    input_hash = Column(String(64), nullable=False)  # SHA256 of input
    
    # Result summary
    claims_generated = Column(Integer, default=0, nullable=False)
    independent_claims = Column(Integer, default=0, nullable=False)
    dependent_claims = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", backref="claim_generations")
    
    def __repr__(self):
        return f"<ClaimGenerationMetadata(project={self.project_id}, claims={self.claims_generated})>"


# ============== Phase 9: Human Feedback & Confidence Calibration Models ==============

class FeedbackType(str, PyEnum):
    """Type of user feedback on AI outputs"""
    HELPFUL = "HELPFUL"
    NOT_HELPFUL = "NOT_HELPFUL"
    AGREE = "AGREE"
    DISAGREE = "DISAGREE"
    NEEDS_REVISION = "NEEDS_REVISION"
    NEEDS_EXPERT = "NEEDS_EXPERT"


class OutputType(str, PyEnum):
    """Type of AI output being rated"""
    SIMILARITY = "SIMILARITY"
    SUMMARY = "SUMMARY"
    DRAFT = "DRAFT"
    CLAIM = "CLAIM"
    RECOMMENDATION = "RECOMMENDATION"
    COMPARATIVE = "COMPARATIVE"


class ConfidenceLevel(str, PyEnum):
    """System confidence level"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"  # Never used for legal/patent contexts


class UserFeedback(Base):
    """
    UserFeedback model - stores human feedback on AI outputs.
    
    Phase 9: NEVER alters original AI outputs.
    Preserves disagreement - no smoothing.
    """
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # What output this feedback is for
    output_id = Column(String(100), nullable=False, index=True)  # e.g., "similarity_1", "claim_5"
    output_type = Column(Enum(OutputType), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Who gave feedback
    user_id = Column(String(100), nullable=True)  # Optional user identifier
    user_role = Column(String(50), nullable=True)  # student / researcher / inventor
    
    # The feedback
    feedback_type = Column(Enum(FeedbackType), nullable=False)
    comment = Column(Text, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_hash = Column(String(64), nullable=True)  # Hashed IP for abuse prevention
    
    # Relationships
    project = relationship("Project", backref="user_feedback")
    
    def __repr__(self):
        return f"<UserFeedback(id={self.id}, type={self.feedback_type}, output={self.output_id})>"


class ConfidenceCalibration(Base):
    """
    ConfidenceCalibration model - tracks confidence state for a project.
    
    Phase 9: Rule-based calibration, transparent and reversible.
    """
    __tablename__ = "confidence_calibrations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Confidence state
    confidence_level = Column(Enum(ConfidenceLevel), default=ConfidenceLevel.LOW, nullable=False)
    
    # Flags
    human_review_recommended = Column(Boolean, default=True, nullable=False)
    disagreement_flag = Column(Boolean, default=False, nullable=False)
    
    # Calibration notes (list stored as JSON)
    calibration_notes = Column(Text, nullable=True)  # JSON array of notes
    
    # Metrics
    total_feedback_count = Column(Integer, default=0, nullable=False)
    disagreement_count = Column(Integer, default=0, nullable=False)
    agreement_count = Column(Integer, default=0, nullable=False)
    evidence_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", backref="confidence_calibration")
    
    def __repr__(self):
        return f"<ConfidenceCalibration(project={self.project_id}, level={self.confidence_level})>"


# ============== Phase 10: Audit & Compliance Models ==============

class ActionType(str, PyEnum):
    """Type of action being audited"""
    PROJECT_CREATED = "PROJECT_CREATED"
    FILE_UPLOADED = "FILE_UPLOADED"
    TEXT_EXTRACTED = "TEXT_EXTRACTED"
    EVIDENCE_RETRIEVED = "EVIDENCE_RETRIEVED"
    SIMILARITY_COMPUTED = "SIMILARITY_COMPUTED"
    NOVELTY_CLASSIFIED = "NOVELTY_CLASSIFIED"
    DRAFT_OPTIMIZED = "DRAFT_OPTIMIZED"
    CLAIMS_GENERATED = "CLAIMS_GENERATED"
    FEEDBACK_SUBMITTED = "FEEDBACK_SUBMITTED"
    CALIBRATION_UPDATED = "CALIBRATION_UPDATED"
    COMPLIANCE_CHECK = "COMPLIANCE_CHECK"
    SYSTEM_STARTUP = "SYSTEM_STARTUP"


class AuditLog(Base):
    """
    AuditLog model - immutable record of system actions.
    
    Phase 10: Full provenance tracking.
    Append-only. No updates or deletions allowed via API.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # What happened
    action_type = Column(Enum(ActionType), nullable=False, index=True)
    
    # What was affected
    entity_type = Column(String(50), nullable=False)  # e.g., "Project", "File", "ClaimDraft"
    entity_id = Column(Integer, nullable=True)        # ID of the affected entity
    
    # Who did it
    user_id = Column(String(100), nullable=True)      # System user ID or IP hash
    
    # When
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Provenance Metadata (JSON)
    # Stores: model_version, prompt_version, input_hash, specific parameters, etc.
    metadata_json = Column(Text, nullable=True)
    
    # Compliance Context
    compliance_mode_active = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<AuditLog(action={self.action_type}, entity={self.entity_type}:{self.entity_id})>"

