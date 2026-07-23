# backend/app/schemas/practice.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import time


class AttemptRecord(BaseModel):
    attempt_id: int
    student_id: str
    alphabet_practiced: str
    predicted_alphabet: str
    is_correct: bool
    confidence: float
    inference_time_ms: float
    timestamp: float = Field(default_factory=time.time)


class StartPracticeRequest(BaseModel):
    student_id: str
    selected_alphabets: Optional[List[str]] = None  # None defaults to A-Z
    auto_next: bool = True


class PracticeAttemptRequest(BaseModel):
    session_id: str
    predicted_alphabet: str
    confidence: float
    inference_time_ms: float


class PracticeAttemptResponse(BaseModel):
    record: AttemptRecord
    is_correct: bool
    expected_alphabet: str
    current_session_accuracy: float
    attempt_count: int
    next_alphabet: Optional[str]
    session_completed: bool


class StudentDashboardResponse(BaseModel):
    student_id: str
    total_practice_attempts: int
    overall_accuracy_percent: float
    average_confidence: float
    daily_practice_streak: int
    most_mistaken_alphabets: Dict[str, int]
    strongest_alphabets: List[str]
    weakest_alphabets: List[str]
    recent_history: List[AttemptRecord]
    