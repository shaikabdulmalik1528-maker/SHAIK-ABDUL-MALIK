from datetime import datetime, timezone
from typing import List, Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.progress import LearnerState, AlphabetLearnerState, AlphabetStateHistory
from app.models.session import AssessmentAttempt, PracticeSession


class ProgressService:

    @staticmethod
    def get_user_learner_states(db: Session, user_id: Any) -> List[AlphabetLearnerState]:
        """
        Retrieves all alphabet learner states for a given user.
        """
        return db.query(AlphabetLearnerState).filter_by(user_id=user_id).all()

    @staticmethod
    def update_learner_state(
        db: Session,
        user_id: Any,
        alphabet: str,
        recent_accuracy: float,
        recent_confidence: float
    ) -> AlphabetLearnerState:
        """
        Evaluates recent performance and updates the learner state machine for a specific alphabet.
        """
        alphabet_clean = alphabet.upper()

        # Fetch or create state record
        state_record = (
            db.query(AlphabetLearnerState)
            .filter_by(user_id=user_id, alphabet=alphabet_clean)
            .first()
        )

        if not state_record:
            state_record = AlphabetLearnerState(
                user_id=user_id,
                alphabet=alphabet_clean,
                current_state=LearnerState.NOT_ATTEMPTED,
                total_attempts=0,
                rolling_accuracy=0.0,
                average_confidence=0.0
            )
            db.add(state_record)
            db.flush()

        state_record.total_attempts += 1

        # Fetch recent attempts joined with practice sessions for this user
        recent_attempts = (
            db.query(AssessmentAttempt)
            .join(PracticeSession, AssessmentAttempt.session_id == PracticeSession.id)
            .filter(PracticeSession.user_id == str(user_id), AssessmentAttempt.alphabet == alphabet_clean)
            .order_by(desc(AssessmentAttempt.timestamp))
            .limit(3)
            .all()
        )

        if recent_attempts:
            accuracies = [float(a.is_correct) for a in recent_attempts]
            confidences = [a.confidence for a in recent_attempts]
            state_record.rolling_accuracy = sum(accuracies) / len(accuracies)
            state_record.average_confidence = sum(confidences) / len(confidences)
        else:
            state_record.rolling_accuracy = recent_accuracy
            state_record.average_confidence = recent_confidence

        old_state = state_record.current_state

        # State Transition Engine Logic
        new_state, reason = ProgressService.evaluate_next_state(
            current_state=old_state,
            total_attempts=state_record.total_attempts,
            rolling_accuracy=state_record.rolling_accuracy,
            average_confidence=state_record.average_confidence,
            last_practiced_at=state_record.last_practiced_at
        )

        state_record.last_practiced_at = datetime.now(timezone.utc)
        state_record.updated_at = datetime.now(timezone.utc)

        # Log transition if state changed
        if old_state != new_state:
            state_record.current_state = new_state
            history_entry = AlphabetStateHistory(
                user_id=user_id,
                alphabet=alphabet_clean,
                from_state=old_state,
                to_state=new_state,
                trigger_reason=reason
            )
            db.add(history_entry)

        db.commit()
        db.refresh(state_record)
        return state_record

    @staticmethod
    def evaluate_next_state(
        current_state: LearnerState,
        total_attempts: int,
        rolling_accuracy: float,
        average_confidence: float,
        last_practiced_at: Optional[datetime]
    ) -> Tuple[LearnerState, str]:
        """
        Determines the state transition based on measurable performance thresholds.
        """
        # Check for inactivity decay
        if last_practiced_at and current_state == LearnerState.MASTERED:
            last_dt = last_practiced_at.replace(tzinfo=timezone.utc) if last_practiced_at.tzinfo is None else last_practiced_at
            days_inactive = (datetime.now(timezone.utc) - last_dt).days
            if days_inactive > 14:
                return LearnerState.NEEDS_REVISION, f"Inactivity threshold exceeded ({days_inactive} days idle)"

        # Performance-based transitions
        if rolling_accuracy >= 0.85 and average_confidence >= 0.80 and total_attempts >= 3:
            return LearnerState.MASTERED, "Consistently high accuracy and model confidence across sessions"

        if rolling_accuracy >= 0.70:
            return LearnerState.IMPROVING, "Solid progress with accuracy >= 70%"

        if rolling_accuracy < 0.50 and total_attempts >= 3:
            return LearnerState.NEEDS_REVISION, "Accuracy dropped below 50% after multiple attempts"

        if total_attempts > 0:
            return LearnerState.LEARNING, "Initial practice attempts recorded"

        return LearnerState.NOT_ATTEMPTED, "No attempts recorded"
    