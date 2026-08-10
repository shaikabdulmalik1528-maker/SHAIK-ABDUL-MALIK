# app/main.py
from fastapi import FastAPI
from app.routers import reports

app = FastAPI(title="Reporting & Insights Module")

# Register the routes from the reports router
app.include_router(reports.router)
