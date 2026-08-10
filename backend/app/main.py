from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    analytics_router,
    assessment_router,
    recommendation_router,
    reports,
    session_router,
)

app = FastAPI(
    title="Sign Language Learning Assessment Platform",
    description="Backend API for real-time sign language recognition, practice tracking, and analytics reporting.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check route
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Sign Language Platform API"}

# Register module routers matching exact prefix definitions
app.include_router(analytics_router.router)
app.include_router(assessment_router.router)
app.include_router(recommendation_router.router)
app.include_router(reports.router)
app.include_router(session_router.router)
