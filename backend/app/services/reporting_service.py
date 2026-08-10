import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, List

class ReportingService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_student_performance_summary(self, student_id: int) -> Dict[str, Any]:
        """Calculates dynamic performance metrics for a specific student directly from DB records."""
        query = f"""
            SELECT 
                s.id as session_id,
                s.created_at,
                a.alphabet,
                a.is_correct,
                a.confidence_score,
                a.inference_time_ms,
                a.misclassified_as
            FROM practice_sessions s
            JOIN attempt_logs a ON s.id = a.session_id
            WHERE s.student_id = {student_id}
        """
        df = pd.read_sql(query, self.db.bind)

        if df.empty:
            return {"error": "No data available for this student."}

        total_sessions = int(df['session_id'].nunique())
        total_attempts = int(len(df))
        overall_accuracy = round(float((df['is_correct'].sum() / total_attempts) * 100), 2)
        
        latest_session_id = df['session_id'].max()
        latest_df = df[df['session_id'] == latest_session_id]
        current_session_accuracy = round(float((latest_df['is_correct'].sum() / len(latest_df)) * 100), 2)

        avg_confidence = round(float(df['confidence_score'].mean() * 100), 2)
        avg_inference_time = round(float(df['inference_time_ms'].mean()), 2)

        alpha_stats = df.groupby('alphabet').agg(
            total=('is_correct', 'count'),
            correct=('is_correct', 'sum')
        )
        alpha_stats['accuracy'] = alpha_stats['correct'] / alpha_stats['total']

        strongest_alphabets = alpha_stats.sort_values(by='accuracy', ascending=False).head(3).index.tolist()
        weakest_alphabets = alpha_stats.sort_values(by='accuracy', ascending=True).head(3).index.tolist()
        most_frequent = alpha_stats.sort_values(by='total', ascending=False).head(3).index.tolist()

        misclassified = df[df['is_correct'] == False]['alphabet'].value_counts()
        most_misclassified = misclassified.head(3).index.tolist()

        recommendations = self._generate_recommendations(
            overall_accuracy, avg_inference_time, weakest_alphabets, most_misclassified
        )

        return {
            "student_id": student_id,
            "total_sessions": total_sessions,
            "total_attempts": total_attempts,
            "overall_accuracy": overall_accuracy,
            "current_session_accuracy": current_session_accuracy,
            "avg_confidence": avg_confidence,
            "avg_inference_time_ms": avg_inference_time,
            "strongest_alphabets": strongest_alphabets,
            "weakest_alphabets": weakest_alphabets,
            "most_frequently_practiced": most_frequent,
            "most_misclassified": most_misclassified,
            "recommendations": recommendations
        }

    def get_session_report(self, session_id: int) -> Dict[str, Any]:
        """Generates automated summary data at the end of a session."""
        query = f"""
            SELECT alphabet, is_correct, confidence_score, inference_time_ms, misclassified_as
            FROM attempt_logs
            WHERE session_id = {session_id}
        """
        df = pd.read_sql(query, self.db.bind)

        if df.empty:
            return {"error": "Session empty or not found."}

        total_attempts = int(len(df))
        session_accuracy = round(float((df['is_correct'].sum() / total_attempts) * 100), 2)
        avg_confidence = round(float(df['confidence_score'].mean() * 100), 2)
        avg_speed = round(float(df['inference_time_ms'].mean()), 2)
        
        missed_letters = df[df['is_correct'] == False]['alphabet'].tolist()

        return {
            "session_id": session_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_attempts": total_attempts,
            "session_accuracy": session_accuracy,
            "avg_confidence": avg_confidence,
            "avg_inference_time_ms": avg_speed,
            "letters_to_review": list(set(missed_letters))
        }

    def _generate_recommendations(self, accuracy: float, speed: float, weakest: List[str], misclassified: List[str]) -> List[str]:
        recs = []
        if accuracy < 75.0:
            recs.append("Focus on slowing down during attempts to improve spatial precision.")
        if speed > 1200:
            recs.append("Practice recognition drills to lower your average inference time.")
        if weakest:
            recs.append(f"Allocate extra time to practice these challenging alphabets: {', '.join(weakest)}.")
        if misclassified:
            recs.append(f"Review common confusion points for: {', '.join(misclassified)}.")
        if not recs:
            recs.append("Great overall performance! Challenge yourself with higher speed drills.")
        return recs
    