from fastapi import APIRouter

from app.services.session_service import SessionService

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

session_service = SessionService()


@router.post("/start/{lesson_id}")
def start_session(lesson_id: int):
    return session_service.start_session(lesson_id)


@router.post("/{session_id}/attempt")
def increment_attempt(session_id: str):
    return session_service.increment_attempt(session_id)


@router.post("/{session_id}/end")
def end_session(session_id: str):
    return session_service.end_session(session_id)


@router.get("/{session_id}")
def get_session(session_id: str):
    return session_service.get_session(session_id)


@router.get("")
def get_all_sessions():
    return session_service.get_all_sessions()