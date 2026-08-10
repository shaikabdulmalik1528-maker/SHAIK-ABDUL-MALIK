import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.session import PracticeSession, AssessmentAttempt, SessionStatus
from app.services.progress_service import ProgressService


class SessionService:

    @staticmethod
    def create_practice_session(db: Session, user_id: Any) -> PracticeSession:
        """
        Creates and starts a new practice session record.
        """
        session = PracticeSession(
            user_id=str(user_id),
            status=SessionStatus.ACTIVE.value,
            start_time=datetime.now(timezone.utc)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def complete_assessment(
        db: Session,
        session_id: str,
        user_id: Any,
        alphabet: str,
        accuracy_score: float,
        confidence_score: float,
        feedback_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Saves the assessment attempt and invokes ProgressService to evaluate state transitions.
        """
        alphabet_clean = alphabet.upper()
        is_correct_val = 1 if accuracy_score >= 0.70 else 0

        # Record the individual attempt
        attempt = AssessmentAttempt(
            session_id=str(session_id),
            alphabet=alphabet_clean,
            is_correct=is_correct_val,
            confidence=confidence_score,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(attempt)

        # Update aggregated metrics on PracticeSession
        session = db.query(PracticeSession).filter_by(id=str(session_id)).first()
        if session:
            session.total_attempts += 1
            if is_correct_val == 1:
                session.correct_attempts += 1
            else:
                session.incorrect_attempts += 1
            
            # Recalculate session accuracy
            session.accuracy = session.correct_attempts / session.total_attempts

        db.commit()
        db.refresh(attempt)

        # Trigger Learner State Machine evaluation
        updated_state = ProgressService.update_learner_state(
            db=db,
            user_id=user_id,
            alphabet=alphabet_clean,
            recent_accuracy=accuracy_score,
            recent_confidence=confidence_score
        )

        return {
            "status": "success",
            "attempt_id": attempt.id,
            "alphabet": alphabet_clean,
            "current_state": updated_state.current_state,
            "rolling_accuracy": round(updated_state.rolling_accuracy, 2),
            "average_confidence": round(updated_state.average_confidence, 2),
            "total_attempts": updated_state.total_attempts
        }

    @staticmethod
    def end_practice_session(db: Session, session_id: str) -> Optional[PracticeSession]:
        """
        Marks a session as completed and sets the ended timestamp & duration.
        """
        session = db.query(PracticeSession).filter_by(id=str(session_id)).first()
        if session:
            now = datetime.now(timezone.utc)
            session.status = SessionStatus.COMPLETED.value
            session.end_time = now
            if session.start_time:
                # Handle tz-aware and tz-naive datetime objects cleanly
                start_dt = session.start_time
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                session.duration_seconds = (now - start_dt).total_seconds()

            db.commit()
            db.refresh(session)
        return session
    