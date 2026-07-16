from fastapi import APIRouter

from app.services.preprocessing_service import PreprocessingService

router = APIRouter(
    prefix="/preprocess",
    tags=["Preprocessing"]
)

service = PreprocessingService()


@router.post("/")
def preprocess_dataset():
    """
    Run the complete preprocessing pipeline.
    """

    result = service.run()

    return result