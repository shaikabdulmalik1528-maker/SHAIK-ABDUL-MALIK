from pydantic import BaseModel, Field
from typing import List, Optional

class LandmarkPoint(BaseModel):
    x: float = Field(..., example=0.5)
    y: float = Field(..., example=0.5)
    z: float = Field(..., example=0.0)
    visibility: Optional[float] = Field(1.0, example=0.98)

class AssessmentPipelineRequest(BaseModel):
    user_id: str = Field(..., min_length=1, example="malik_01")
    session_id: str = Field(..., min_length=1, example="sess_100")
    target_alphabet: str = Field(..., min_length=1, max_length=1, example="A")
    hand_landmarks: List[LandmarkPoint] = Field(..., min_items=21, max_items=21)
    pose_landmarks: Optional[List[LandmarkPoint]] = None
    client_timestamp: Optional[float] = None