from fastapi import FastAPI
from app.routers import session_router  # Include new router

app = FastAPI(title="Sign Language Assessment API")

# Register the sessions router
app.include_router(session_router.router)