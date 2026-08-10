import string
from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.progress import AlphabetLearnerState, LearnerState


class RecommendationService:

    # Base weight priority assigned to each Learner State
    STATE_PRIORITY_WEIGHTS = {
        LearnerState.NEEDS_REVISION: 100,  # Highest priority (Requires immediate practice)
        LearnerState.LEARNING: 75,        # High priority (In active learning phase)
        LearnerState.IMPROVING: 50,       # Moderate priority (Building consistency)
        LearnerState.NOT_ATTEMPTED: 30,   # Low priority (Unstarted items)
        LearnerState.MASTERED: 10         # Lowest priority (Periodic spaced review)
    }

    @classmethod
    def get_recommendations(cls, db: Session, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Generates adaptive practice recommendations based on alphabet learner states,
        rolling accuracy, and inactivity thresholds rather than single assessment scores.
        """
        # Fetch current states for the user
        user_states = db.query(AlphabetLearnerState).filter_by(user_id=user_id).all()
        state_map = {s.alphabet: s for s in user_states}

        now = datetime.now(timezone.utc)
        recommendations = []

        # Process all alphabets (A through Z)
        for letter in string.ascii_uppercase:
            record = state_map.get(letter)

            if not record:
                state = LearnerState.NOT_ATTEMPTED
                days_idle = 30
                rolling_acc = 0.0
            else:
                state = record.current_state
                # Calculate inactivity duration in days
                if record.last_practiced_at:
                    # Handle both timezone-aware and naive datetime objects
                    last_practiced = record.last_practiced_at
                    if last_practiced.tzinfo is None:
                        last_practiced = last_practiced.replace(tzinfo=timezone.utc)
                    days_idle = (now - last_practiced).days
                else:
                    days_idle = 30
                
                rolling_acc = record.rolling_accuracy

            # Calculate dynamic priority score
            base_weight = cls.STATE_PRIORITY_WEIGHTS[state]
            recency_modifier = min(days_idle * 2, 30)       # Up to +30 points for longer inactivity
            accuracy_penalty = (1.0 - rolling_acc) * 20     # Up to +20 points for lower accuracy

            priority_score = base_weight + recency_modifier + accuracy_penalty

            recommendations.append({
                "alphabet": letter,
                "current_state": state.value,
                "priority_score": round(priority_score, 2),
                "rolling_accuracy": round(rolling_acc, 2),
                "days_idle": days_idle,
                "reason": f"State: {state.value} | Idle: {days_idle}d | Rolling Acc: {int(rolling_acc * 100)}%"
            })

        # Sort descending by priority score and return top recommendations
        recommendations.sort(key=lambda item: item["priority_score"], reverse=True)
        return recommendations[:limit]
    