# backend/app/schemas/feedback_review.py
from pydantic import BaseModel
from typing import List, Dict, Optional


class FeedbackRuleResult(BaseModel):
    rule_name: str
    passed: bool
    correction_message: Optional[str] = None


class StructuredFeedbackResponse(BaseModel):
    expected_gesture: str
    predicted_gesture: str
    is_correct: bool
    overall_message: str
    detailed_corrections: List[str]


class PracticeReviewResponse(BaseModel):
    session_id: str
    student_id: str
    overall_score_percent: float
    total_attempts: int
    correct_gestures: List[str]
    incorrect_gestures: List[str]
    confidence_trend: List[float]
    most_common_mistakes: Dict[str, int]
    gesture_specific_feedback: Dict[str, List[str]]
    recommended_next_gestures: List[str]
    