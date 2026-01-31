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




