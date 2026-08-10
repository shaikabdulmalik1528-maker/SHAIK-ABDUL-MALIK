import csv
import io
from typing import Dict, Any


class ExportUtils:

    @staticmethod
    def generate_student_csv(report_data: Dict[str, Any]) -> str:
        """
        Converts student performance report dictionary into a clean CSV string format.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["=== STUDENT PERFORMANCE REPORT ==="])
        writer.writerow(["User ID", report_data.get("user_id")])
        writer.writerow(["Generated At", report_data.get("generated_at")])
        writer.writerow([])

        writer.writerow(["--- OVERALL METRICS ---"])
        writer.writerow(["Total Practice Sessions", report_data.get("total_practice_sessions")])
        writer.writerow(["Total Attempts", report_data.get("total_attempts")])
        writer.writerow(["Overall Accuracy (%)", f"{report_data.get('overall_accuracy', 0) * 100:.1f}%"])
        writer.writerow(["Current Session Accuracy (%)", f"{report_data.get('current_session_accuracy', 0) * 100:.1f}%"])
        writer.writerow(["Average Confidence (%)", f"{report_data.get('average_confidence', 0) * 100:.1f}%"])
        writer.writerow(["Average Inference Time (ms)", report_data.get("average_inference_time_ms")])
        writer.writerow([])

        writer.writerow(["--- ALPHABET BREAKDOWN ---"])
        writer.writerow(["Strongest Alphabets", ", ".join(report_data.get("strongest_alphabets", [])) or "None"])
        writer.writerow(["Weakest Alphabets", ", ".join(report_data.get("weakest_alphabets", [])) or "None"])
        writer.writerow(["Most Frequently Practiced", ", ".join(report_data.get("most_frequently_practiced", [])) or "None"])
        writer.writerow(["Most Commonly Misclassified", ", ".join(report_data.get("most_commonly_misclassified", [])) or "None"])
        writer.writerow([])

        writer.writerow(["--- PERSONALIZED RECOMMENDATIONS ---"])
        for rec in report_data.get("personalized_recommendations", []):
            writer.writerow([f"• Alphabet: {rec.get('alphabet')}", f"State: {rec.get('current_state')}", f"Reason: {rec.get('reason')}"])

        return output.getvalue()

    @staticmethod
    def generate_session_csv(session_report: Dict[str, Any]) -> str:
        """
        Converts session report dictionary into CSV string format.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["=== END OF SESSION REPORT ==="])
        writer.writerow(["Session ID", session_report.get("session_id")])
        writer.writerow(["User ID", session_report.get("user_id")])
        writer.writerow(["Start Time", session_report.get("start_time")])
        writer.writerow(["End Time", session_report.get("end_time")])
        writer.writerow(["Duration (seconds)", session_report.get("duration_seconds")])
        writer.writerow([])

        writer.writerow(["--- SESSION SUMMARY ---"])
        writer.writerow(["Total Attempts", session_report.get("total_attempts")])
        writer.writerow(["Correct Attempts", session_report.get("correct_attempts")])
        writer.writerow(["Incorrect Attempts", session_report.get("incorrect_attempts")])
        writer.writerow(["Session Accuracy (%)", f"{session_report.get('session_accuracy', 0) * 100:.1f}%"])
        writer.writerow(["Average Confidence (%)", f"{session_report.get('average_confidence', 0) * 100:.1f}%"])

        return output.getvalue()
