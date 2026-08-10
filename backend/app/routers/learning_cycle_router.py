from typing import Any, Dict
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import inspect

from app.database.database import get_db
from app.services.session_service import SessionService
from app.services.progress_service import ProgressService
from app.services.recommendation_service import RecommendationService
from app.services.report_service import ReportService


def get_current_user():
    class MockUser:
        id = 1
        username = "autonomous_student"
    return MockUser()


class AutoInferenceRequest(BaseModel):
    session_id: str
    target_alphabet: str
    predicted_alphabet: str
    confidence: float
    inference_time_ms: float = 45.0


router = APIRouter(prefix="/cycle", tags=["Autonomous Learning Cycle"])


@router.post("/start-cycle")
def start_autonomous_learning_cycle(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    if hasattr(SessionService, "create_practice_session"):
        session = SessionService.create_practice_session(db, user_id=current_user.id)
    elif hasattr(SessionService, "create_session"):
        session = SessionService.create_session(db, user_id=current_user.id)
    else:
        session = SessionService.start_session(db, user_id=current_user.id)
    
    recommendations = RecommendationService.get_recommendations(db, user_id=current_user.id, limit=1)
    recommended_alphabet = recommendations[0] if recommendations else {"alphabet": "A", "current_state": "NOT_ATTEMPTED"}

    return {
        "message": "Autonomous learning session initialized.",
        "session_id": str(session.id),
        "user_id": str(current_user.id),
        "status": session.status,
        "current_recommendation": recommended_alphabet
    }


@router.post("/process-attempt")
def process_gesture_attempt_and_adapt(
    payload: AutoInferenceRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    is_correct = 1 if payload.target_alphabet.upper() == payload.predicted_alphabet.upper() else 0

    # Dynamic inspection of SessionService logging methods
    attempt = None
    for method_name in ["record_assessment_attempt", "log_assessment_attempt", "add_assessment_attempt", "record_attempt", "create_assessment_attempt"]:
        if hasattr(SessionService, method_name):
            attempt_func = getattr(SessionService, method_name)
            try:
                attempt = attempt_func(
                    db=db,
                    session_id=payload.session_id,
                    alphabet=payload.target_alphabet.upper(),
                    is_correct=is_correct,
                    confidence=payload.confidence
                )
                break
            except TypeError:
                continue

    if attempt is None:
        from app.models.session import AssessmentAttempt
        attempt = AssessmentAttempt(
            session_id=payload.session_id,
            alphabet=payload.target_alphabet.upper(),
            is_correct=is_correct,
            confidence=payload.confidence
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

    # Dynamic parameter binding for ProgressService
    progress_func = getattr(ProgressService, "update_learner_state", getattr(ProgressService, "update_learner_progress", None))
    
    if progress_func:
        sig = inspect.signature(progress_func)
        params = sig.parameters
        
        kw_args = {}
        if "db" in params:
            kw_args["db"] = db
        if "user_id" in params:
            kw_args["user_id"] = current_user.id
        if "alphabet" in params:
            kw_args["alphabet"] = payload.target_alphabet.upper()
        if "is_correct" in params:
            kw_args["is_correct"] = is_correct
        elif "correct" in params:
            kw_args["correct"] = bool(is_correct)
        if "confidence" in params:
            kw_args["confidence"] = payload.confidence

        try:
            updated_state = progress_func(**kw_args)
        except Exception:
            # Positional fallback matching typical service signatures
            updated_state = progress_func(db, current_user.id, payload.target_alphabet.upper(), is_correct, payload.confidence)
    else:
        updated_state = None

    if is_correct:
        feedback = f"Great job! Your sign for '{payload.target_alphabet}' was accurate ({payload.confidence*100:.1f}% confidence)."
    else:
        feedback = f"Keep practicing! You performed '{payload.predicted_alphabet}', but target was '{payload.target_alphabet}'."

    next_recommendations = RecommendationService.get_recommendations(db, user_id=current_user.id, limit=1)
    next_rec = next_recommendations[0] if next_recommendations else None

    return {
        "assessment": {
            "attempt_id": str(getattr(attempt, "id", "")),
            "target_alphabet": payload.target_alphabet.upper(),
            "predicted_alphabet": payload.predicted_alphabet.upper(),
            "is_correct": bool(is_correct),
            "confidence": payload.confidence,
            "inference_time_ms": payload.inference_time_ms
        },
        "feedback": feedback,
        "updated_learner_state": {
            "alphabet": getattr(updated_state, "alphabet", payload.target_alphabet.upper()),
            "current_state": getattr(updated_state, "current_state", "LEARNING"),
            "rolling_accuracy": getattr(updated_state, "rolling_accuracy", 0.0),
            "average_confidence": getattr(updated_state, "average_confidence", 0.0),
            "total_attempts": getattr(updated_state, "total_attempts", 1)
        },
        "next_recommendation": next_rec
    }


@router.post("/end-cycle/{session_id}")
def end_autonomous_learning_cycle(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    ended_session = None
    for method_name in ["end_practice_session", "complete_session", "close_session", "end_session"]:
        if hasattr(SessionService, method_name):
            end_func = getattr(SessionService, method_name)
            try:
                ended_session = end_func(db, session_id=session_id)
                break
            except TypeError:
                continue

    if not ended_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    session_summary = ReportService.generate_session_report(db, session_id=session_id)

    return {
        "message": "Session completed successfully.",
        "session_summary": session_summary
    }
