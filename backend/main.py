from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tutor_service import IntelligentTutorService

app = FastAPI(title="Sign Language Intelligent Tutor API")

# Enable CORS for frontend integration later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tutor = IntelligentTutorService(db_path="app_data.db")

class AssessmentRequest(BaseModel):
    user_id: str
    session_id: str
    target_alphabet: str
    predicted_alphabet: str
    confidence_score: float

@app.post("/api/v1/assess")
def evaluate_gesture(request: AssessmentRequest):
    """
    Core End-to-End Workflow:
    Receives prediction -> Assesses -> Updates Learner Profile -> Returns Feedback & Recommendations.
    """
    try:
        response = tutor.process_prediction_event(
            user_id=request.user_id,
            session_id=request.session_id,
            target=request.target_alphabet,
            predicted=request.predicted_alphabet,
            confidence=request.confidence_score
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/recommendations/{user_id}")
def get_recommendations(user_id: str, limit: int = 5):
    """Returns prioritized alphabets with explicit learning rationales."""
    try:
        return tutor.generate_recommendations(user_id=user_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dashboard/{user_id}")
def get_dashboard(user_id: str):
    """Returns analytics dashboard data."""
    try:
        return tutor.get_analytics_dashboard(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    