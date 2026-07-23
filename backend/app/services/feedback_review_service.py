# backend/app/services/feedback_review_service.py
import numpy as np
from typing import List, Dict, Type
from abc import ABC, abstractmethod

from app.schemas.feedback_review import (
    FeedbackRuleResult,
    StructuredFeedbackResponse,
    PracticeReviewResponse
)
from app.services.practice_service import PracticeSession


# ==========================================
# TASK 1: EXTENSIBLE FEEDBACK ENGINE
# ==========================================

class BaseFeedbackRule(ABC):
    """Abstract base class for landmark evaluation rules."""
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, expected: str, predicted: str, landmarks: np.ndarray) -> FeedbackRuleResult:
        pass


class FingerExtensionRule(BaseFeedbackRule):
    """Rule checking if specific fingers should be bent or extended."""
    @property
    def name(self) -> str:
        return "FingerExtensionCheck"

    def evaluate(self, expected: str, predicted: str, landmarks: np.ndarray) -> FeedbackRuleResult:
        if expected.upper() == predicted.upper():
            return FeedbackRuleResult(rule_name=self.name, passed=True)

        if landmarks is None or landmarks.size != 63:
            return FeedbackRuleResult(
                rule_name=self.name,
                passed=False,
                correction_message="Hand keypoints incomplete. Position hand clearly inside webcam frame."
            )

        pts = landmarks.reshape(21, 3)
        # Check index finger tip (8) vs index PIP joint (6)
        index_extended = pts[8][1] < pts[6][1]
        # Check middle finger tip (12) vs middle PIP joint (10)
        middle_extended = pts[12][1] < pts[10][1]

        fist_gestures = ["A", "S", "E", "M", "N"]
        pointing_gestures = ["D", "I", "1"]

        if expected in fist_gestures and (index_extended or middle_extended):
            return FeedbackRuleResult(
                rule_name=self.name,
                passed=False,
                correction_message=f"For gesture '{expected}', curl your fingers into a tighter fist."
            )

        if expected in pointing_gestures and not index_extended:
            return FeedbackRuleResult(
                rule_name=self.name,
                passed=False,
                correction_message=f"For gesture '{expected}', extend your index finger straight up."
            )

        return FeedbackRuleResult(rule_name=self.name, passed=True)


class PalmOrientationRule(BaseFeedbackRule):
    """Rule evaluating hand center position relative to wrist origin."""
    @property
    def name(self) -> str:
        return "PalmOrientationCheck"

    def evaluate(self, expected: str, predicted: str, landmarks: np.ndarray) -> FeedbackRuleResult:
        if expected.upper() == predicted.upper():
            return FeedbackRuleResult(rule_name=self.name, passed=True)

        if landmarks is None or landmarks.size != 63:
            return FeedbackRuleResult(rule_name=self.name, passed=True)

        pts = landmarks.reshape(21, 3)
        wrist = pts[0]
        middle_mcp = pts[9]

        if abs(middle_mcp[2] - wrist[2]) > 0.3:
            return FeedbackRuleResult(
                rule_name=self.name,
                passed=False,
                correction_message="Rotate palm parallel to the camera lens for better alignment."
            )

        return FeedbackRuleResult(rule_name=self.name, passed=True)


class FeedbackEngine:
    """
    Feedback Engine managing registered rules.
    New rules can be added via register_rule() without modifying existing evaluation code.
    """
    def __init__(self):
        self.rules: List[BaseFeedbackRule] = []

    def register_rule(self, rule: BaseFeedbackRule):
        self.rules.append(rule)

    def generate_feedback(
        self,
        expected_gesture: str,
        predicted_gesture: str,
        landmarks: np.ndarray
    ) -> StructuredFeedbackResponse:
        is_correct = (expected_gesture.upper() == predicted_gesture.upper())

        if is_correct:
            return StructuredFeedbackResponse(
                expected_gesture=expected_gesture,
                predicted_gesture=predicted_gesture,
                is_correct=True,
                overall_message=f"✓ Correct! Your '{expected_gesture}' sign matches expected geometry.",
                detailed_corrections=[]
            )

        corrections = []
        for rule in self.rules:
            result = rule.evaluate(expected_gesture, predicted_gesture, landmarks)
            if not result.passed and result.correction_message:
                corrections.append(f"💡 [{result.rule_name}] {result.correction_message}")

        if not corrections:
            corrections.append(f"💡 You performed '{predicted_gesture}', but expected '{expected_gesture}'. Re-check reference image.")

        return StructuredFeedbackResponse(
            expected_gesture=expected_gesture,
            predicted_gesture=predicted_gesture,
            is_correct=False,
            overall_message=f"✗ Incorrect sign geometry for '{expected_gesture}'.",
            detailed_corrections=corrections
        )


# ==========================================
# TASK 2: PRACTICE REVIEW SCREEN GENERATOR
# ==========================================

class PracticeReviewGenerator:
    @staticmethod
    def generate_review(session: PracticeSession, feedback_engine: FeedbackEngine) -> PracticeReviewResponse:
        records = session.attempts
        if not records:
            raise ValueError("No records found in session to generate review.")

        total_attempts = len(records)
        correct_list = [r.alphabet_practiced for r in records if r.is_correct]
        incorrect_list = [r.alphabet_practiced for r in records if not r.is_correct]

        confidence_trend = [round(r.confidence, 4) for r in records]

        from collections import Counter
        mistake_counts = dict(Counter(incorrect_list))

        gesture_feedback: Dict[str, List[str]] = {}
        for r in records:
            if not r.is_correct:
                dummy_landmarks = np.zeros(63)
                fb = feedback_engine.generate_feedback(r.alphabet_practiced, r.predicted_alphabet, dummy_landmarks)
                if r.alphabet_practiced not in gesture_feedback:
                    gesture_feedback[r.alphabet_practiced] = []
                gesture_feedback[r.alphabet_practiced].extend(fb.detailed_corrections)

        gesture_stats = {}
        for r in records:
            g = r.alphabet_practiced
            if g not in gesture_stats:
                gesture_stats[g] = {"total": 0, "correct": 0}
            gesture_stats[g]["total"] += 1
            if r.is_correct:
                gesture_stats[g]["correct"] += 1

        weakest = [
            g for g, stat in gesture_stats.items()
            if (stat["correct"] / stat["total"]) < 1.0
        ]

        if not weakest:
            recommendations = ["All gestures mastered! Try full A-Z speed practice."]
        else:
            recommendations = [f"Focus practice on gesture '{g}'" for g in set(weakest)]

        return PracticeReviewResponse(
            session_id=session.session_id,
            student_id=session.student_id,
            overall_score_percent=session.session_accuracy,
            total_attempts=total_attempts,
            correct_gestures=correct_list,
            incorrect_gestures=incorrect_list,
            confidence_trend=confidence_trend,
            most_common_mistakes=mistake_counts,
            gesture_specific_feedback=gesture_feedback,
            recommended_next_gestures=recommendations
        )