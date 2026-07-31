# backend/app/api/practice.py
from fastapi import APIRouter, HTTPException
import uuid

from app.schemas.practice import (
    StartPracticeRequest,
    PracticeAttemptRequest,
    PracticeAttemptResponse,
    StudentDashboardResponse
)
from app.services.practice_service import PracticeService

router = APIRouter(prefix="/practice", tags=["Practice & Analytics"])
practice_service = PracticeService()


@router.post("/start")
def start_practice_session(req: StartPracticeRequest):
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    session = practice_service.start_session(
        session_id=session_id,
        student_id=req.student_id,
        alphabets=req.selected_alphabets,
        auto_next=req.auto_next
    )
    return {
        "session_id": session.session_id,
        "student_id": session.student_id,
        "first_alphabet": session.current_alphabet,
        "total_letters": len(session.alphabets),
        "auto_next": session.auto_next
    }


@router.post("/attempt", response_model=PracticeAttemptResponse)
def evaluate_attempt(req: PracticeAttemptRequest):
    try:
        res = practice_service.record_attempt(
            session_id=req.session_id,
            predicted_alphabet=req.predicted_alphabet,
            confidence=req.confidence,
            inference_time_ms=req.inference_time_ms
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard/{student_id}", response_model=StudentDashboardResponse)
def get_student_dashboard(student_id: str):
    return practice_service.get_student_dashboard(student_id)
