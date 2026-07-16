from fastapi import APIRouter

from app.services.practice_service import PracticeService

router = APIRouter(
    prefix="/practice",
    tags=["Practice"]
)

practice_service = PracticeService()


@router.post("/start/{lesson_id}")
def start_practice(lesson_id: int):
    return practice_service.start_practice(lesson_id)


@router.get("/detect")
def detect_hand():
    return practice_service.detect_hand()


@router.get("/landmarks")
def extract_landmarks():
    return practice_service.extract_landmarks()


@router.post("/predict/{session_id}")
def predict(session_id: str):
    return practice_service.predict_sign(session_id)


@router.post("/end/{session_id}")
def end_practice(session_id: str):
    return practice_service.end_practice(session_id)