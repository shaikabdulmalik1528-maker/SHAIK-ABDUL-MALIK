from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.prediction import router as prediction_router
from app.api.lessons import router as lessons_router
from app.api.practice import router as practice_router
from app.api.session import router as session_router
from app.api.preprocessing import router as preprocessing_router

app = FastAPI()

app.include_router(health_router)
app.include_router(prediction_router)
app.include_router(lessons_router)
app.include_router(practice_router)
app.include_router(session_router)
app.include_router(preprocessing_router)