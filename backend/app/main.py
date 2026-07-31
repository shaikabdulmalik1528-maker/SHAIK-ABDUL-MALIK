# backend/app/main.py
from fastapi import FastAPI
from app.api import predict, practice

app = FastAPI(title="Sign Language Platform API", version="1.0.0")

# Include Routers
app.include_router(predict.router)
app.include_router(practice.router)

@app.get("/")
def read_root():
    return {"message": "Sign Language AI Platform Backend Active"}