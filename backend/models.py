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
    """Analysis status enum - Phase 1 only uses NOT_STARTED"""
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"  # Reserved for future phases
    BLOCKED = "BLOCKED"  # Reserved for future phases


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
    
    def __repr__(self):
        return f"<File(id={self.id}, original_filename='{self.original_filename}')>"


class AnalysisState(Base):
    """
    AnalysisState model - tracks honest state of project analysis.
    
    Phase 1 Behavior:
    - analysis_status is ALWAYS 'NOT_STARTED'
    - notes clearly state that AI is not implemented
    - No fake progress or percentages
    """
    __tablename__ = "analysis_states"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)
    
    # State flags (automatically computed)
    idea_received = Column(Boolean, default=False, nullable=False)
    files_uploaded = Column(Boolean, default=False, nullable=False)
    
    # Analysis status - always NOT_STARTED in Phase 1
    analysis_status = Column(
        Enum(AnalysisStatus), 
        default=AnalysisStatus.NOT_STARTED, 
        nullable=False
    )
    
    # Honest notes about current limitations
    notes = Column(
        Text, 
        default="AI analysis not implemented. Phase 1 provides data persistence only.",
        nullable=False
    )
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="analysis_state")
    
    def __repr__(self):
        return f"<AnalysisState(project_id={self.project_id}, status={self.analysis_status})>"
