from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from app.database.database import Base

class AlphabetStateEnum(str, enum.Enum):
    NOT_ATTEMPTED = "Not Attempted"
    NEEDS_REVISION = "Needs Revision"
    LEARNING = "Learning"
    IMPROVING = "Improving"
    MASTERED = "Mastered"

class LearnerAlphabetState(Base):
    __tablename__ = "learner_alphabet_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    alphabet_char = Column(String(5), nullable=False, index=True)
    current_state = Column(Enum(AlphabetStateEnum), default=AlphabetStateEnum.NOT_ATTEMPTED, nullable=False)
    
    total_attempts = Column(Integer, default=0, nullable=False)
    successful_attempts = Column(Integer, default=0, nullable=False)
    accuracy_rate = Column(Float, default=0.0, nullable=False)
    avg_confidence = Column(Float, default=0.0, nullable=False)
    avg_attempts_to_correct = Column(Float, default=0.0, nullable=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearnerStateHistory(Base):
    __tablename__ = "learner_state_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    alphabet_char = Column(String(5), nullable=False)
    previous_state = Column(Enum(AlphabetStateEnum), nullable=False)
    new_state = Column(Enum(AlphabetStateEnum), nullable=False)
    session_id = Column(Integer, nullable=True)
    transition_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    