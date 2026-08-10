from app.database.database import Base

# Try importing User from models.user, or fallback to models.session
try:
    from app.models.user import User
except ImportError:
    try:
        from app.models.session import User
    except ImportError:
        User = None

from app.models.session import PracticeSession
from app.models.learner_state import LearnerAlphabetState, LearnerStateHistory
from app.models.progress import LearnerState, AlphabetLearnerState, AlphabetStateHistory

__all__ = [
    "Base",
    "PracticeSession",
    "LearnerAlphabetState",
    "LearnerStateHistory",
    "LearnerState",
    "AlphabetLearnerState",
    "AlphabetStateHistory",
]

if User:
    __all__.append("User")
    