import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.database.database import Base# Adjust import path to your project layout

class SessionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"

class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    status = Column(String, default=SessionStatus.ACTIVE.value, nullable=False)
    
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    # Aggregated metrics (computed when session terminates)
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    incorrect_attempts = Column(Integer, default=0, nullable=False)
    accuracy = Column(Float, default=0.0, nullable=False)
    avg_confidence = Column(Float, default=0.0, nullable=False)

    # Relationship to attempts
    attempts = relationship("AssessmentAttempt", back_populates="session", cascade="all, delete-orphan")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("practice_sessions.id"), nullable=False)
    
    alphabet = Column(String, nullable=False)
    is_correct = Column(Integer, nullable=False)  # 1 for correct, 0 for incorrect
    confidence = Column(Float, nullable=False)     # e.g., 0.0 to 1.0 or percentage
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("PracticeSession", back_populates="attempts")