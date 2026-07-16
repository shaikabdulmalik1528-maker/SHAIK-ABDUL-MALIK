# backend/app/api/prediction.py
import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.schemas.prediction import PredictionResponse
from app.services.gesture_service import GestureService

# 1. Define the router with the prefix "/predict"
router = APIRouter(prefix="/predict", tags=["Inference"])

# 2. Dependency injection to get the running instance of GestureService
_SERVICE_INSTANCE = GestureService()

def get_gesture_service() -> GestureService:
    return _SERVICE_INSTANCE

# 3. Define the POST endpoint at the root of the prefix (which makes it POST /predict)
@router.post("", response_model=PredictionResponse)
async def predict_gesture(
    file: UploadFile = File(...),
    service: GestureService = Depends(get_gesture_service)
):
    # Read the uploaded file bytes into a numpy array
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image upload.")

    # Run raw image prediction through your self-contained service and engine
    result = service.predict_image(image)
    
    # Return structured schema response
    return PredictionResponse(
        gesture=result.gesture,
        confidence=result.confidence,
        model_version=result.model_version,
        processing_time=result.inference_time_ms,
        hand_detected=result.hand_detected,
        landmarks_validated=result.landmarks_validated
    )
    