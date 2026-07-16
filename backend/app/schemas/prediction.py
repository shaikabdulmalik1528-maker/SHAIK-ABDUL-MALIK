# backend/app/schemas/prediction.py
from pydantic import BaseModel

class PredictionResponse(BaseModel):
    gesture: str                 # This matches your model output
    confidence: float
    model_version: str
    processing_time: float       # This maps to inference_time_ms
    hand_detected: bool
    landmarks_validated: bool
    