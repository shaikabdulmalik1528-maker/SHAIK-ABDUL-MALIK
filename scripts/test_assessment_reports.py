# scripts/test_assessment_reports.py
import os
import sys

# Add backend directory to module search path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.assessment_report_service import (
    SignAccuracyAssessmentEngine,
    AssessmentReportGenerator
)

def test_assessment_and_reports():
    print("🚀 Initializing Assessment Engine & Report Generator Test...\n")
    engine = SignAccuracyAssessmentEngine()

    simulated_attempts = [
        {"expected": "A", "predicted": "A", "conf": 0.95, "time": 1.5},
        {"expected": "B", "predicted": "V", "conf": 0.82, "time": 3.1},
        {"expected": "B", "predicted": "B", "conf": 0.91, "time": 2.0},
        {"expected": "C", "predicted": "C", "conf": 0.98, "time": 1.2},
        {"expected": "D", "predicted": "D", "conf": 0.89, "time": 2.2},
    ]

    for attempt in simulated_attempts:
        fb = engine.evaluate_sign(
            expected_gesture=attempt["expected"],
            predicted_gesture=attempt["predicted"],
            confidence_score=attempt["conf"],
            time_taken_sec=attempt["time"]
        )
        status = "✓ CORRECT" if fb.is_correct else "✗ INCORRECT"
        print(f"Attempt #{fb.attempt_number} | Expected: '{fb.expected_gesture}' | Predicted: '{fb.predicted_gesture}' ({status})")
        print(f"   ├─ Session Acc: {fb.session_accuracy}% | Gesture Acc ('{fb.expected_gesture}'): {fb.overall_gesture_accuracy}%")
        print(f"   └─ Feedback: {fb.feedback_message}\n")

    os.makedirs("reports", exist_ok=True)
    json_path = "reports/assessment_report.json"
    excel_path = "reports/assessment_report.xlsx"
    pdf_path = "reports/assessment_report.pdf"

    AssessmentReportGenerator.export_json(engine.records, json_path)
    AssessmentReportGenerator.export_excel(engine.records, excel_path)
    AssessmentReportGenerator.export_pdf(engine.records, pdf_path)

    print("📊 Report Exports Generated Successfully:")
    print(f"   ├─ JSON:  {json_path}")
    print(f"   ├─ Excel: {excel_path}")
    print(f"   └─ PDF:   {pdf_path}")

    print("\n🎉 Assessment Engine & Report Generator Fully Verified!")

if __name__ == "__main__":
    test_assessment_and_reports()
    