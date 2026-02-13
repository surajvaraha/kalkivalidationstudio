from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class TaskType(str, enum.Enum):
    KALKI = "KALKI"
    UNKNOWN = "UNKNOWN"

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class ValidationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    SKIPPED = "SKIPPED" # For rows that might be empty or invalid
    IN_PROGRESS = "IN_PROGRESS"

class RejectionReasonMaster(Base):
    """Unique rejection reason text - defined once, used across stages."""
    __tablename__ = "rejection_reason_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reason_text = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stage_links = relationship("StageReasonLink", back_populates="master", cascade="all, delete-orphan")


class StageReasonLink(Base):
    """Maps a master reason to a stage (many-to-many)."""
    __tablename__ = "stage_reason_link"

    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(Integer, ForeignKey("rejection_reason_master.id"), nullable=False)
    stage = Column(String, nullable=False, index=True)  # moisture, start, mid, 90, end
    display_order = Column(Integer, default=0)

    master = relationship("RejectionReasonMaster", back_populates="stage_links")


class ValidationTask(Base):
    __tablename__ = "validation_tasks"

    id = Column(String, primary_key=True) # UUID
    filename = Column(String)
    task_type = Column(SAEnum(TaskType), default=TaskType.UNKNOWN)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    batches = relationship("BatchRow", back_populates="task", cascade="all, delete-orphan")

class BatchRow(Base):
    __tablename__ = "batch_rows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("validation_tasks.id"))
    row_index = Column(Integer) # Original 0-based index in Excel
    
    # We store the full raw row data as JSON
    raw_data = Column(JSON, default={})
    
    # We store the validation decisions as JSON
    # Structure: { "wood_moisture": { "status": "Approved", "reason": "...", ... }, ... }
    validation_data = Column(JSON, default={})
    
    status = Column(SAEnum(ValidationStatus), default=ValidationStatus.PENDING)
    
    task = relationship("ValidationTask", back_populates="batches")
