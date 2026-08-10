import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, Enum as SQLEnum

from app.database.database import Base


class LearnerState(str, enum.Enum):
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    LEARNING = "LEARNING"
    IMPROVING = "IMPROVING"
    MASTERED = "MASTERED"
    NEEDS_REVISION = "NEEDS_REVISION"


class AlphabetLearnerState(Base):
    __tablename__ = "alphabet_learner_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    alphabet = Column(String(1), nullable=False)
    current_state = Column(SQLEnum(LearnerState), nullable=False, default=LearnerState.NOT_ATTEMPTED)
    total_attempts = Column(Integer, default=0)
    rolling_accuracy = Column(Float, default=0.0)      # Weighted accuracy of recent N sessions
    average_confidence = Column(Float, default=0.0)    # Vision engine confidence score [0.0 - 1.0]
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('user_id', 'alphabet', name='unique_user_alphabet_state'),
    )


class AlphabetStateHistory(Base):
    __tablename__ = "alphabet_state_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    alphabet = Column(String(1), nullable=False)
    from_state = Column(SQLEnum(LearnerState), nullable=False)
    to_state = Column(SQLEnum(LearnerState), nullable=False)
    trigger_reason = Column(String(255), nullable=True)
    transitioned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    