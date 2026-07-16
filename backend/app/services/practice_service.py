from app.services.session_service import SessionService


class PracticeService:

    def __init__(self):
        self.session_service = SessionService()

    def start_practice(self, lesson_id: int):
        session = self.session_service.start_session(lesson_id)

        return {
            "message": "Practice Started",
            "camera": "Ready",
            "session": session
        }

    def detect_hand(self):
        return {
            "status": "Hand Detected (Placeholder)"
        }

    def extract_landmarks(self):
        return {
            "status": "Landmarks Extracted (Placeholder)"
        }

    def predict_sign(self, session_id: str):
        self.session_service.increment_attempt(session_id)

        return {
            "prediction": "A",
            "confidence": 0.0,
            "status": "Placeholder Prediction"
        }

    def end_practice(self, session_id: str):
        session = self.session_service.end_session(session_id)

        return {
            "message": "Practice Completed",
            "session": session
        }