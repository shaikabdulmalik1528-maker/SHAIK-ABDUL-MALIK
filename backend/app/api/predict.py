# backend/app/api/predict.py
import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.schemas.predict import PredictionResponse
from app.services.gesture_service import GestureService

router = APIRouter(prefix="/predict", tags=["Inference"])

# Dependency injection for the service layer
_SERVICE_INSTANCE = GestureService()

def get_gesture_service() -> GestureService:
    return _SERVICE_INSTANCE

@router.post("", response_model=PredictionResponse)
async def predict_gesture(
    file: UploadFile = File(...),
    service: GestureService = Depends(get_gesture_service)
):
    # 1. Read uploaded file bytes
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image upload.")

    # 2. Get prediction from service
    result = service.predict_image(image)
    
    # 3. Return schema-conforming response
    return PredictionResponse(
        gesture=result.gesture,
        confidence=result.confidence,
        model_version=result.model_version,
        processing_time=result.inference_time_ms,
        hand_detected=result.hand_detected,
        landmarks_validated=result.landmarks_validated
    )