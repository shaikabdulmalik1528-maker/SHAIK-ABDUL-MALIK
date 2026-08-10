from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.session_service import SessionService


def get_current_user():
    class MockUser:
        id = 1
        username = "test_user"
    return MockUser()


router = APIRouter(prefix="/sessions", tags=["Practice Sessions"])


# --- Pydantic Schemas ---

class CompleteAssessmentRequest(BaseModel):
    session_id: str
    alphabet: str
    accuracy_score: float
    confidence_score: float
    feedback_data: Optional[Dict[str, Any]] = None


class StartSessionResponse(BaseModel):
    session_id: str
    user_id: str
    started_at: str
    is_active: bool


# --- API Routes ---

@router.post("/start", response_model=StartSessionResponse)
def start_session(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Starts a new practice session for the logged-in user.
    """
    session = SessionService.create_practice_session(db, user_id=current_user.id)
    return StartSessionResponse(
        session_id=str(session.id),
        user_id=str(session.user_id),
        started_at=session.start_time.isoformat(),
        is_active=(session.status == "ACTIVE")
    )


@router.post("/complete-assessment")
def complete_assessment(
    payload: CompleteAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Ingests an assessment result, saves attempt metrics, and updates learner state.
    """
    result = SessionService.complete_assessment(
        db=db,
        session_id=payload.session_id,
        user_id=current_user.id,
        alphabet=payload.alphabet,
        accuracy_score=payload.accuracy_score,
        confidence_score=payload.confidence_score,
        feedback_data=payload.feedback_data
    )
    return result


@router.post("/end/{session_id}")
def end_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Closes an active practice session.
    """
    session = SessionService.end_practice_session(db, session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"message": f"Session {session_id} ended successfully"}
