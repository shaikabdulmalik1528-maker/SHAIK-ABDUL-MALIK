from datetime import datetime
from uuid import uuid4


class SessionService:
    def __init__(self):
        self.sessions = {}

    def start_session(self, lesson_id: int):
        session_id = str(uuid4())

        self.sessions[session_id] = {
            "session_id": session_id,
            "lesson_id": lesson_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "attempts": 0,
            "status": "In Progress"
        }

        return self.sessions[session_id]

    def increment_attempt(self, session_id: str):
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        self.sessions[session_id]["attempts"] += 1
        return self.sessions[session_id]

    def end_session(self, session_id: str):
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        self.sessions[session_id]["end_time"] = datetime.now().isoformat()
        self.sessions[session_id]["status"] = "Completed"

        return self.sessions[session_id]

    def get_session(self, session_id: str):
        return self.sessions.get(session_id, {"error": "Session not found"})

    def get_all_sessions(self):
        return list(self.sessions.values())