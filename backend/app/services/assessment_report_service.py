# backend/app/services/assessment_report_service.py
import os
import time
import json
import pandas as pd
from typing import List, Dict
from pydantic import BaseModel, Field

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class AssessmentRecord(BaseModel):
    attempt_number: int
    expected_gesture: str
    predicted_gesture: str
    is_correct: bool
    confidence_score: float
    time_taken_sec: float
    session_accuracy: float
    overall_gesture_accuracy: float
    timestamp: float = Field(default_factory=time.time)


class AssessmentFeedback(BaseModel):
    expected_gesture: str
    predicted_gesture: str
    is_correct: bool
    confidence_score: float
    overall_gesture_accuracy: float
    attempt_number: int
    time_taken_sec: float
    session_accuracy: float
    feedback_message: str


class AssessmentReportSummary(BaseModel):
    total_assessment_attempts: int
    correct_attempts: int
    incorrect_attempts: int
    overall_assessment_score: float
    average_confidence: float
    average_response_time_sec: float
    most_difficult_gestures: List[str]
    gesture_wise_performance: Dict[str, Dict[str, float]]
    improvement_across_attempts: List[Dict[str, float]]


class SignAccuracyAssessmentEngine:
    def __init__(self):
        self.records: List[AssessmentRecord] = []

    def evaluate_sign(
        self,
        expected_gesture: str,
        predicted_gesture: str,
        confidence_score: float,
        time_taken_sec: float
    ) -> AssessmentFeedback:
        attempt_number = len(self.records) + 1
        is_correct = (expected_gesture.upper() == predicted_gesture.upper())

        correct_so_far = sum(1 for r in self.records if r.is_correct) + (1 if is_correct else 0)
        session_accuracy = round((correct_so_far / attempt_number) * 100, 2)

        same_gesture_records = [r for r in self.records if r.expected_gesture.upper() == expected_gesture.upper()]
        gesture_attempts = len(same_gesture_records) + 1
        gesture_correct = sum(1 for r in same_gesture_records if r.is_correct) + (1 if is_correct else 0)
        overall_gesture_accuracy = round((gesture_correct / gesture_attempts) * 100, 2)

        record = AssessmentRecord(
            attempt_number=attempt_number,
            expected_gesture=expected_gesture.upper(),
            predicted_gesture=predicted_gesture.upper(),
            is_correct=is_correct,
            confidence_score=round(confidence_score, 4),
            time_taken_sec=round(time_taken_sec, 2),
            session_accuracy=session_accuracy,
            overall_gesture_accuracy=overall_gesture_accuracy,
            timestamp=time.time()
        )
        self.records.append(record)

        if is_correct:
            msg = f"✓ Perfect! Your sign for '{expected_gesture}' matches accurately with {confidence_score*100:.1f}% confidence."
        else:
            msg = f"✗ Incorrect. Performed '{predicted_gesture}', but expected '{expected_gesture}'. Adjust hand shape and retry."

        return AssessmentFeedback(
            expected_gesture=record.expected_gesture,
            predicted_gesture=record.predicted_gesture,
            is_correct=record.is_correct,
            confidence_score=record.confidence_score,
            overall_gesture_accuracy=record.overall_gesture_accuracy,
            attempt_number=record.attempt_number,
            time_taken_sec=record.time_taken_sec,
            session_accuracy=record.session_accuracy,
            feedback_message=msg
        )


class AssessmentReportGenerator:
    @staticmethod
    def generate_summary(records: List[AssessmentRecord]) -> AssessmentReportSummary:
        if not records:
            raise ValueError("No assessment records found to generate report.")

        total_attempts = len(records)
        correct_count = sum(1 for r in records if r.is_correct)
        incorrect_count = total_attempts - correct_count
        overall_score = round((correct_count / total_attempts) * 100, 2)

        avg_confidence = round(sum(r.confidence_score for r in records) / total_attempts, 4)
        avg_time = round(sum(r.time_taken_sec for r in records) / total_attempts, 2)

        gesture_stats: Dict[str, Dict[str, float]] = {}
        for r in records:
            g = r.expected_gesture
            if g not in gesture_stats:
                gesture_stats[g] = {"total": 0, "correct": 0}
            gesture_stats[g]["total"] += 1
            if r.is_correct:
                gesture_stats[g]["correct"] += 1

        for g, s in gesture_stats.items():
            s["accuracy_percent"] = round((s["correct"] / s["total"]) * 100, 2)

        difficult = [g for g, s in gesture_stats.items() if s["accuracy_percent"] < 60.0]

        improvement = []
        for i, r in enumerate(records, start=1):
            window_correct = sum(1 for x in records[:i] if x.is_correct)
            window_acc = round((window_correct / i) * 100, 2)
            improvement.append({"attempt": i, "cumulative_accuracy": window_acc})

        return AssessmentReportSummary(
            total_assessment_attempts=total_attempts,
            correct_attempts=correct_count,
            incorrect_attempts=incorrect_count,
            overall_assessment_score=overall_score,
            average_confidence=avg_confidence,
            average_response_time_sec=avg_time,
            most_difficult_gestures=difficult,
            gesture_wise_performance=gesture_stats,
            improvement_across_attempts=improvement
        )

    @classmethod
    def export_json(cls, records: List[AssessmentRecord], file_path: str) -> str:
        summary = cls.generate_summary(records)
        data = {
            "summary": summary.model_dump(),
            "raw_records": [r.model_dump() for r in records]
        }
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        return file_path

    @classmethod
    def export_excel(cls, records: List[AssessmentRecord], file_path: str) -> str:
        summary = cls.generate_summary(records)
        df_records = pd.DataFrame([r.model_dump() for r in records])
        summary_dict = {
            "Metric": [
                "Total Attempts", "Correct Attempts", "Incorrect Attempts",
                "Overall Score (%)", "Average Confidence", "Avg Response Time (s)", "Most Difficult Gestures"
            ],
            "Value": [
                summary.total_assessment_attempts,
                summary.correct_attempts,
                summary.incorrect_attempts,
                f"{summary.overall_assessment_score}%",
                f"{summary.average_confidence * 100:.1f}%",
                f"{summary.average_response_time_sec}s",
                ", ".join(summary.most_difficult_gestures) if summary.most_difficult_gestures else "None"
            ]
        }
        df_summary = pd.DataFrame(summary_dict)

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            df_records.to_excel(writer, sheet_name="Detailed Records", index=False)

        return file_path

    @classmethod
    def export_pdf(cls, records: List[AssessmentRecord], file_path: str) -> str:
        summary = cls.generate_summary(records)
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1A365D'))
        story.append(Paragraph("Sign Language Assessment & Performance Report", title_style))
        story.append(Spacer(1, 12))

        summary_data = [
            ["Metric", "Value"],
            ["Total Assessment Attempts", str(summary.total_assessment_attempts)],
            ["Correct / Incorrect", f"{summary.correct_attempts} / {summary.incorrect_attempts}"],
            ["Overall Assessment Score", f"{summary.overall_assessment_score}%"],
            ["Average Confidence", f"{summary.average_confidence * 100:.1f}%"],
            ["Average Response Time", f"{summary.average_response_time_sec} s"],
            ["Difficult Gestures", ", ".join(summary.most_difficult_gestures) if summary.most_difficult_gestures else "None"]
        ]

        t_summary = Table(summary_data, colWidths=[200, 250])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        story.append(t_summary)
        story.append(Spacer(1, 18))

        story.append(Paragraph("Attempt Records Summary", styles['Heading2']))
        story.append(Spacer(1, 8))

        rec_table_data = [["#", "Expected", "Predicted", "Result", "Confidence", "Time"]]
        for r in records:
            res_str = "CORRECT" if r.is_correct else "INCORRECT"
            rec_table_data.append([
                str(r.attempt_number), r.expected_gesture, r.predicted_gesture,
                res_str, f"{r.confidence_score*100:.1f}%", f"{r.time_taken_sec}s"
            ])

        t_rec = Table(rec_table_data, colWidths=[30, 70, 70, 80, 80, 60])
        t_rec.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t_rec)

        doc.build(story)
        return file_path
    