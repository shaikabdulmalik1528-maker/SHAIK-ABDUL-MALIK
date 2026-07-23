# backend/app/services/practice_service.py
import time
from typing import Dict, List, Optional
from collections import Counter
from app.schemas.practice import AttemptRecord, StudentDashboardResponse


class PracticeSession:
    def __init__(self, session_id: str, student_id: str, alphabets: List[str], auto_next: bool = True):
        self.session_id = session_id
        self.student_id = student_id
        self.alphabets = alphabets
        self.auto_next = auto_next
        self.current_index = 0
        self.attempts: List[AttemptRecord] = []

    @property
    def current_alphabet(self) -> Optional[str]:
        if self.current_index < len(self.alphabets):
            return self.alphabets[self.current_index]
        return None

    @property
    def total_attempts(self) -> int:
        return len(self.attempts)

    @property
    def correct_attempts(self) -> int:
        return sum(1 for a in self.attempts if a.is_correct)

    @property
    def session_accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return round((self.correct_attempts / self.total_attempts) * 100, 2)

    @property
    def is_completed(self) -> bool:
        return self.current_index >= len(self.alphabets)


class PracticeService:
    def __init__(self):
        self.active_sessions: Dict[str, PracticeSession] = {}
        # Persistent storage across sessions grouped by student_id
        self.student_history: Dict[str, List[AttemptRecord]] = {}

    def start_session(self, session_id: str, student_id: str, alphabets: Optional[List[str]] = None, auto_next: bool = True) -> PracticeSession:
        if not alphabets:
            alphabets = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
            
        session = PracticeSession(session_id, student_id, alphabets, auto_next)
        self.active_sessions[session_id] = session
        return session

    def record_attempt(
        self,
        session_id: str,
        predicted_alphabet: str,
        confidence: float,
        inference_time_ms: float
    ) -> Dict:
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        expected = session.current_alphabet
        if not expected:
            raise ValueError("Practice session is already completed.")

        is_correct = (expected.upper() == predicted_alphabet.upper())
        attempt_id = session.total_attempts + 1

        record = AttemptRecord(
            attempt_id=attempt_id,
            student_id=session.student_id,
            alphabet_practiced=expected,
            predicted_alphabet=predicted_alphabet,
            is_correct=is_correct,
            confidence=round(confidence, 4),
            inference_time_ms=round(inference_time_ms, 2),
            timestamp=time.time()
        )

        session.attempts.append(record)

        # Store in overall student history
        if session.student_id not in self.student_history:
            self.student_history[session.student_id] = []
        self.student_history[session.student_id].append(record)

        # Advance to next question if correct or auto_next is enabled
        if is_correct or session.auto_next:
            session.current_index += 1

        return {
            "record": record,
            "is_correct": is_correct,
            "expected_alphabet": expected,
            "current_session_accuracy": session.session_accuracy,
            "attempt_count": session.total_attempts,
            "next_alphabet": session.current_alphabet,
            "session_completed": session.is_completed
        }

    def get_student_dashboard(self, student_id: str) -> StudentDashboardResponse:
        history = self.student_history.get(student_id, [])

        if not history:
            return StudentDashboardResponse(
                student_id=student_id,
                total_practice_attempts=0,
                overall_accuracy_percent=0.0,
                average_confidence=0.0,
                daily_practice_streak=0,
                most_mistaken_alphabets={},
                strongest_alphabets=[],
                weakest_alphabets=[],
                recent_history=[]
            )

        total_attempts = len(history)
        correct_count = sum(1 for h in history if h.is_correct)
        overall_accuracy = round((correct_count / total_attempts) * 100, 2)
        avg_confidence = round(sum(h.confidence for h in history) / total_attempts, 4)

        # Mistake analysis
        mistakes = [h.alphabet_practiced for h in history if not h.is_correct]
        most_mistaken = dict(Counter(mistakes).most_common(5))

        # Gesture-wise accuracy breakdown
        stats = {}
        for h in history:
            g = h.alphabet_practiced
            if g not in stats:
                stats[g] = {"total": 0, "correct": 0}
            stats[g]["total"] += 1
            if h.is_correct:
                stats[g]["correct"] += 1

        strongest = [g for g, s in stats.items() if (s["correct"] / s["total"]) >= 0.8]
        weakest = [g for g, s in stats.items() if (s["correct"] / s["total"]) < 0.5]

        # Calculate active streak (distinct days practiced)
        unique_days = {time.strftime("%Y-%m-%d", time.localtime(h.timestamp)) for h in history}
        daily_streak = len(unique_days)

        return StudentDashboardResponse(
            student_id=student_id,
            total_practice_attempts=total_attempts,
            overall_accuracy_percent=overall_accuracy,
            average_confidence=avg_confidence,
            daily_practice_streak=daily_streak,
            most_mistaken_alphabets=most_mistaken,
            strongest_alphabets=strongest,
            weakest_alphabets=weakest,
            recent_history=history[-10:]  # Return last 10 attempts
        )
        