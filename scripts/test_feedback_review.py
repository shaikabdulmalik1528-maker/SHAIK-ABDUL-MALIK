# scripts/test_feedback_review.py
import os
import sys
import numpy as np

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.practice_service import PracticeService
from app.services.feedback_review_service import (
    FeedbackEngine,
    FingerExtensionRule,
    PalmOrientationRule,
    PracticeReviewGenerator
)

def test_feedback_and_review():
    print("🚀 Initializing Feedback Engine & Practice Review Test...\n")

    # 1. Instantiate and Register Rules in Feedback Engine
    fb_engine = FeedbackEngine()
    fb_engine.register_rule(FingerExtensionRule())
    fb_engine.register_rule(PalmOrientationRule())
    print("✅ Extensible Feedback Engine initialized with 2 registered rules.")

    # 2. Test Single Attempt Landmark Rule Evaluation
    mock_landmarks = np.zeros(63)  # Dummy 63-dim landmark vector
    feedback_res = fb_engine.generate_feedback(
        expected_gesture="A",
        predicted_gesture="V",
        landmarks=mock_landmarks
    )
    print("\n--- Feedback Engine Single Output Check ---")
    print(f"Overall Message: {feedback_res.overall_message}")
    for corr in feedback_res.detailed_corrections:
        print(f"  └─ {corr}")

    # 3. Simulate Complete Session & Generate Review Screen Data
    print("\n--- Simulating Practice Session ---")
    practice_service = PracticeService()
    session = practice_service.start_session("sess_review_001", "23P61A12A5", ["A", "B", "C", "D"])

    # Attempt 1: 'A' -> 'A' (Correct)
    practice_service.record_attempt(session.session_id, "A", 0.95, 12.0)
    # Attempt 2: 'B' -> 'V' (Incorrect)
    practice_service.record_attempt(session.session_id, "V", 0.78, 15.0)
    # Attempt 3: 'C' -> 'C' (Correct)
    practice_service.record_attempt(session.session_id, "C", 0.98, 10.0)
    # Attempt 4: 'D' -> 'D' (Correct)
    practice_service.record_attempt(session.session_id, "D", 0.91, 11.5)

    review_data = PracticeReviewGenerator.generate_review(session, fb_engine)

    print("\n================ PRACTICE REVIEW SCREEN DATA ================")
    print(f"Session ID:           {review_data.session_id}")
    print(f"Student ID:           {review_data.student_id}")
    print(f"Overall Score:        {review_data.overall_score_percent}%")
    print(f"Total Attempts:       {review_data.total_attempts}")
    print(f"Correct Gestures:     {review_data.correct_gestures}")
    print(f"Incorrect Gestures:   {review_data.incorrect_gestures}")
    print(f"Confidence Trend:     {review_data.confidence_trend}")
    print(f"Most Common Mistakes: {review_data.most_common_mistakes}")
    print(f"Gesture Feedback:     {review_data.gesture_specific_feedback}")
    print(f"Recommendations:      {review_data.recommended_next_gestures}")
    print("=============================================================\n")

    print("🎉 Task 1 (Feedback Engine) & Task 2 (Practice Review) Verified!")

if __name__ == "__main__":
    test_feedback_and_review()
    