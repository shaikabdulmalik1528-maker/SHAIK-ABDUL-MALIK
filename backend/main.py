from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Ensure the backend directory is in the Python path for relative imports
sys.path.append(str(Path(__file__).resolve().parent))

from app.core.exceptions import register_exception_handlers
from app.routers import assessment_router, analytics_router, recommendation_router

app = FastAPI(
    title="Sign Language Platform - Production Backend",
    version="2.0.0",
    description="Production-Ready Modular Architecture for Intelligent Assessment & Continuous Learning Engine"
)

# Enable CORS for React Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Centralized Exception Handlers
register_exception_handlers(app)

# Register Modular Routers with FastAPI
app.include_router(assessment_router.router)
app.include_router(analytics_router.router)
app.include_router(recommendation_router.router)

@app.get("/", tags=["Health Check"])
def health_check():
    return {
        "status": "ONLINE",
        "system": "Sign Language Platform API v2.0.0",
        "message": "Production Backend Services Running"
    }
    