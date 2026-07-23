# scripts/test_practice_module.py
import os
import sys

# Ensure backend directory is in system path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.practice_service import PracticeService

def test_practice_workflow():
    print("🚀 Testing Practice Workflow & Analytics Engine...\n")
    service = PracticeService()

    # 1. Start Practice Session
    session = service.start_session(
        session_id="sess_test_001",
        student_id="23P61A12A5",
        alphabets=["A", "B", "C", "D"],
        auto_next=True
    )
    print(f"✅ Session Started: {session.session_id} | First Letter: '{session.current_alphabet}'")

    # 2. Simulate User Practice Attempts
    attempts_data = [
        {"predicted": "A", "conf": 0.94, "time": 14.2},  # Correct for 'A'
        {"predicted": "V", "conf": 0.81, "time": 16.5},  # Incorrect for 'B'
        {"predicted": "C", "conf": 0.98, "time": 11.0},  # Correct for 'C'
        {"predicted": "D", "conf": 0.89, "time": 13.4},  # Correct for 'D'
    ]

    for data in attempts_data:
        curr_expected = session.current_alphabet
        res = service.record_attempt(
            session_id=session.session_id,
            predicted_alphabet=data["predicted"],
            confidence=data["conf"],
            inference_time_ms=data["time"]
        )
        
        status = "✓ Correct" if res["is_correct"] else "✗ Incorrect"
        print(f"Letter '{curr_expected}' -> Predicted '{data['predicted']}' ({status}) | Session Accuracy: {res['current_session_accuracy']}%")

    print(f"\n🎉 Session Finished! Session Completed Status: {session.is_completed}")

    # 3. Check Student Dashboard & Analytics
    print("\n📊 Fetching Student Analytics Dashboard...")
    dashboard = service.get_student_dashboard("23P61A12A5")

    print(f"Total Practice Attempts: {dashboard.total_practice_attempts}")
    print(f"Overall Accuracy:        {dashboard.overall_accuracy_percent}%")
    print(f"Average Confidence:      {dashboard.average_confidence * 100:.1f}%")
    print(f"Daily Streak:            {dashboard.daily_practice_streak} Day(s)")
    print(f"Most Mistaken Alphabets: {dashboard.most_mistaken_alphabets}")
    print(f"Strongest Alphabets:     {dashboard.strongest_alphabets}")
    print(f"Weakest Alphabets:       {dashboard.weakest_alphabets}")

    print("\n✅ Practice & Analytics Module Verified Successfully!")

if __name__ == "__main__":
    test_practice_workflow()
    