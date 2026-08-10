from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.progress import AlphabetLearnerState, AlphabetStateHistory
from app.services.progress_service import ProgressService


# Mock user dependency until auth module is configured
def get_current_user():
    class MockUser:
        id = 1
        username = "test_user"
    return MockUser()


router = APIRouter(prefix="/analytics", tags=["Analytics & Learner State"])


# --- Pydantic Schemas ---

class LearnerStateResponse(BaseModel):
    alphabet: str
    current_state: str
    total_attempts: int
    rolling_accuracy: float
    average_confidence: float
    last_practiced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StateHistoryResponse(BaseModel):
    id: int
    alphabet: str
    from_state: str
    to_state: str
    trigger_reason: Optional[str] = None
    transitioned_at: datetime

    class Config:
        from_attributes = True


class AnalyticsSummaryResponse(BaseModel):
    total_alphabets_attempted: int
    mastered_count: int
    improving_count: int
    learning_count: int
    needs_revision_count: int
    not_attempted_count: int
    overall_accuracy: float


# --- API Routes ---

@router.get("/learner-states", response_model=List[LearnerStateResponse])
def get_learner_dashboard_states(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Fetches current learning states for every alphabet for the logged-in user.
    Used by the learner dashboard to display status badges and progress indicators.
    """
    states = ProgressService.get_user_learner_states(db, user_id=current_user.id)
    return states


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Aggregates overall user progress metrics across all alphabets.
    """
    states = db.query(AlphabetLearnerState).filter_by(user_id=current_user.id).all()
    
    counts = {
        "MASTERED": 0,
        "IMPROVING": 0,
        "LEARNING": 0,
        "NEEDS_REVISION": 0,
        "NOT_ATTEMPTED": 26 - len(states)  # Unrecorded letters default to NOT_ATTEMPTED
    }
    
    total_acc = 0.0
    attempted_count = 0

    for s in states:
        state_key = s.current_state.value if hasattr(s.current_state, "value") else str(s.current_state)
        counts[state_key] = counts.get(state_key, 0) + 1
        
        if s.total_attempts > 0:
            total_acc += s.rolling_accuracy
            attempted_count += 1

    overall_accuracy = (total_acc / attempted_count) if attempted_count > 0 else 0.0

    return AnalyticsSummaryResponse(
        total_alphabets_attempted=attempted_count,
        mastered_count=counts.get("MASTERED", 0),
        improving_count=counts.get("IMPROVING", 0),
        learning_count=counts.get("LEARNING", 0),
        needs_revision_count=counts.get("NEEDS_REVISION", 0),
        not_attempted_count=counts.get("NOT_ATTEMPTED", 0),
        overall_accuracy=round(overall_accuracy, 2)
    )


@router.get("/state-history/{alphabet}", response_model=List[StateHistoryResponse])
def get_alphabet_state_history(
    alphabet: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Returns the full transition audit trail for a specific alphabet (e.g., 'A').
    """
    history = (
        db.query(AlphabetStateHistory)
        .filter_by(user_id=current_user.id, alphabet=alphabet.upper())
        .order_by(AlphabetStateHistory.transitioned_at.desc())
        .all()
    )
    return history
