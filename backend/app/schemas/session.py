from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class SessionCreate(BaseModel):
    user_id: str

class AttemptCreate(BaseModel):
    alphabet: str
    is_correct: bool
    confidence: float = Field(..., ge=0.0, le=1.0)

class AttemptResponse(BaseModel):
    id: str
    session_id: str
    alphabet: str
    is_correct: bool
    confidence: float
    timestamp: datetime

    class Config:
        from_attributes = True

class SessionSummaryResponse(BaseModel):
    id: str
    user_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    total_attempts: int
    correct_attempts: int
    incorrect_attempts: int
    accuracy: float
    avg_confidence: float

    class Config:
        from_attributes = True
        