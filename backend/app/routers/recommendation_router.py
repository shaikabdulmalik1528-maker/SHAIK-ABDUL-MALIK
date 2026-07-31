from fastapi import APIRouter, status
import time
from app.services.tutor_service import UnifiedTutorService

router = APIRouter(prefix="/api/v1/recommendation", tags=["Recommendation Engine"])
tutor_service = UnifiedTutorService()

@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_recommendations(user_id: str):
    recs = tutor_service.get_recommendations(user_id)
    return {
        "success": True,
        "data": recs,
        "timestamp": time.time()
    }