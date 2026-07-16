from pydantic import BaseModel

class PredictionResponse(BaseModel):
    gesture: str
    confidence: float
    model_version: str
    processing_time: float  # Map to inference_time_ms
    hand_detected: bool
    landmarks_validated: bool
    