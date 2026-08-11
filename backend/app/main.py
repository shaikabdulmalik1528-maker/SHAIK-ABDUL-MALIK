from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    session_router,
    analytics_router,
    recommendation_router,
    report_router,
    learning_cycle_router
)

app = FastAPI(
    title="Sign Language Platform API",
    version="1.0.0",
    description="Backend services for Learner State Engine & Autonomous Learning Cycle"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred while processing your request.",
            "details": str(exc)
        }
    )

app.include_router(session_router.router)
app.include_router(analytics_router.router)
app.include_router(recommendation_router.router)
app.include_router(report_router.router)
app.include_router(learning_cycle_router.router)
