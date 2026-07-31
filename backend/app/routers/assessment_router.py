from fastapi import APIRouter, status
import time
from app.schemas.assessment import AssessmentPipelineRequest
from app.services.validation_service import LandmarkValidationService
from app.services.tutor_service import UnifiedTutorService
from app.core.logger import logger

router = APIRouter(prefix="/api/v1/assessment", tags=["Assessment Engine"])
tutor_service = UnifiedTutorService()

@router.post("/process", status_code=status.HTTP_200_OK)
async def process_full_assessment(payload: AssessmentPipelineRequest):
    start_time = time.time()
    logger.info(f"Assessment request: user={payload.user_id}, target={payload.target_alphabet}")

    # 1. Input Validation Layer
    LandmarkValidationService.validate_frame_quality(
        hand_landmarks=payload.hand_landmarks,
        pose_landmarks=payload.pose_landmarks
    )

    # 2. Model Inference Simulation
    predicted_alphabet = payload.target_alphabet
    confidence_score = 0.94
    inference_time_ms = (time.time() - start_time) * 1000

    # Convert landmarks to list of dicts safely
    raw_pts = [pt.model_dump() if hasattr(pt, 'model_dump') else dict(pt) for pt in payload.hand_landmarks]

    # 3. Store Attempt, Update Learner Profile & Analytics
    result = tutor_service.process_assessment_attempt(
        user_id=payload.user_id,
        session_id=payload.session_id,
        target=payload.target_alphabet,
        predicted=predicted_alphabet,
        confidence=confidence_score,
        inference_time_ms=inference_time_ms,
        raw_landmarks=raw_pts
    )

    return {
        "success": True,
        "data": result,
        "timestamp": time.time()
    }