from typing import List, Any
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.recommendation_service import RecommendationService


# Mock user dependency until auth module is configured
def get_current_user():
    class MockUser:
        id = 1
        username = "test_user"
    return MockUser()


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


# --- Pydantic Schema ---

class RecommendationItem(BaseModel):
    alphabet: str
    current_state: str
    priority_score: float
    rolling_accuracy: float
    days_idle: int
    reason: str


# --- API Route ---

@router.get("/", response_model=List[RecommendationItem])
def get_recommendations(
    limit: int = Query(default=5, ge=1, le=26),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    Generates state-driven practice recommendations for the learner.
    Prioritizes items in NEEDS_REVISION, LEARNING, or IMPROVING states.
    """
    return RecommendationService.get_recommendations(
        db=db,
        user_id=current_user.id,
        limit=limit
    )
    