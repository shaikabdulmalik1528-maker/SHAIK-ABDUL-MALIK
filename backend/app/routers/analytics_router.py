from fastapi import APIRouter, status
import time
from app.services.tutor_service import UnifiedTutorService

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Dashboard"])
tutor_service = UnifiedTutorService()

@router.get("/dashboard/{user_id}", status_code=status.HTTP_200_OK)
async def get_dashboard(user_id: str):
    metrics = tutor_service.get_dashboard_metrics(user_id)
    return {
        "success": True,
        "data": metrics,
        "timestamp": time.time()
    }