import sqlite3
import hashlib
import time
import uuid
import string
from typing import Dict, List, Any
from app.core.exceptions import DuplicateAssessmentError
from app.core.logger import logger

class UnifiedTutorService:
    def __init__(self, db_path: str = "app_data.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS practice_attempts (
                    id TEXT PRIMARY KEY,
                    request_hash TEXT UNIQUE,
                    user_id TEXT,
                    session_id TEXT,
                    target_alphabet TEXT,
                    predicted_alphabet TEXT,
                    confidence_score REAL,
                    is_correct INTEGER,
                    inference_time_ms REAL,
                    timestamp REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learner_profiles (
                    user_id TEXT,
                    alphabet TEXT,
                    total_attempts INTEGER DEFAULT 0,
                    total_correct INTEGER DEFAULT 0,
                    consecutive_correct INTEGER DEFAULT 0,
                    consecutive_incorrect INTEGER DEFAULT 0,
                    avg_confidence REAL DEFAULT 0.0,
                    mastery_level REAL DEFAULT 0.0,
                    last_practiced_at REAL,
                    PRIMARY KEY (user_id, alphabet)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS confusion_matrix (
                    user_id TEXT,
                    expected_alphabet TEXT,
                    predicted_alphabet TEXT,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, expected_alphabet, predicted_alphabet)
                )
            """)
            conn.commit()

    def process_assessment_attempt(
        self, user_id: str, session_id: str, target: str, 
        predicted: str, confidence: float, inference_time_ms: float,
        raw_landmarks: list
    ) -> Dict[str, Any]:
        
        target = target.upper()
        predicted = predicted.upper()
        is_correct = (target == predicted)
        now_epoch = time.time()

        # Extract coordinate safely
        first_pt = raw_landmarks[0] if raw_landmarks else {"x": 0.0}
        if isinstance(first_pt, dict):
            first_x = first_pt.get("x", 0.0)
        else:
            first_x = getattr(first_pt, "x", 0.0)

        hash_str = f"{user_id}_{session_id}_{target}_{predicted}_{confidence:.4f}_{first_x:.3f}"
        request_hash = hashlib.sha256(hash_str.encode()).hexdigest()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Check for duplicates
            cursor.execute("SELECT id FROM practice_attempts WHERE request_hash = ?", (request_hash,))
            if cursor.fetchone():
                raise DuplicateAssessmentError("Duplicate gesture attempt detected. Request rejected.")

            # Seed profiles for A-Z if new user
            for char in string.ascii_uppercase:
                cursor.execute("INSERT OR IGNORE INTO learner_profiles (user_id, alphabet) VALUES (?, ?)", (user_id, char))

            cursor.execute("SELECT * FROM learner_profiles WHERE user_id = ? AND alphabet = ?", (user_id, target))
            row = cursor.fetchone()

            tot_attempts = (row["total_attempts"] or 0) + 1
            tot_correct = (row["total_correct"] or 0) + (1 if is_correct else 0)
            cons_correct = ((row["consecutive_correct"] or 0) + 1) if is_correct else 0
            cons_incorrect = ((row["consecutive_incorrect"] or 0) + 1) if not is_correct else 0

            alpha = 0.3
            prev_avg = row["avg_confidence"] or 0.0
            new_avg_conf = confidence if tot_attempts == 1 else ((1 - alpha) * prev_avg + (alpha * confidence))

            acc = tot_correct / tot_attempts
            streak_bonus = min(cons_correct * 0.05, 0.20)
            mastery_score = max(0.0, min(1.0, (acc * 0.5) + streak_bonus + (new_avg_conf * 0.3)))

            cursor.execute("""
                UPDATE learner_profiles 
                SET total_attempts = ?, total_correct = ?, consecutive_correct = ?,
                    consecutive_incorrect = ?, avg_confidence = ?, mastery_level = ?, last_practiced_at = ?
                WHERE user_id = ? AND alphabet = ?
            """, (tot_attempts, tot_correct, cons_correct, cons_incorrect, new_avg_conf, mastery_score, now_epoch, user_id, target))

            if not is_correct:
                cursor.execute("""
                    INSERT INTO confusion_matrix (user_id, expected_alphabet, predicted_alphabet, count)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(user_id, expected_alphabet, predicted_alphabet)
                    DO UPDATE SET count = count + 1
                """, (user_id, target, predicted))

            attempt_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO practice_attempts 
                (id, request_hash, user_id, session_id, target_alphabet, predicted_alphabet, confidence_score, is_correct, inference_time_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (attempt_id, request_hash, user_id, session_id, target, predicted, confidence, 1 if is_correct else 0, inference_time_ms, now_epoch))

            conn.commit()

        recommendations = self.get_recommendations(user_id)

        return {
            "assessment": {
                "attempt_id": attempt_id,
                "target_alphabet": target,
                "predicted_alphabet": predicted,
                "confidence_score": round(confidence, 4),
                "is_correct": is_correct,
                "inference_time_ms": round(inference_time_ms, 2)
            },
            "updated_profile": {
                "mastery_score": round(mastery_score, 2),
                "total_attempts": tot_attempts,
                "consecutive_correct": cons_correct
            },
            "next_recommendations": recommendations
        }

    def get_recommendations(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        recommendations = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM learner_profiles WHERE user_id = ?", (user_id,))
            profiles = cursor.fetchall()

            for p in profiles:
                alph = p["alphabet"]
                mastery = p["mastery_level"] or 0.0
                last_time = p["last_practiced_at"]
                
                priority_score = (1.0 - mastery) * 40.0
                rationale = f"Low mastery level ({int(mastery * 100)}%)."
                reason_cat = "LOW_MASTERY"

                if not last_time:
                    priority_score = 50.0
                    reason_cat = "NOT_PRACTICED_RECENTLY"
                    rationale = "Has not been practiced yet."

                recommendations.append({
                    "alphabet": alph,
                    "priority_score": round(priority_score, 2),
                    "reason_category": reason_cat,
                    "rationale": rationale
                })

        recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
        return recommendations[:limit]

    def get_dashboard_metrics(self, user_id: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total_attempts FROM practice_attempts WHERE user_id = ?", (user_id,))
            tot_att = cursor.fetchone()["total_attempts"]

            cursor.execute("SELECT COUNT(DISTINCT session_id) as total_sessions FROM practice_attempts WHERE user_id = ?", (user_id,))
            tot_sess = cursor.fetchone()["total_sessions"]

            cursor.execute("SELECT AVG(mastery_level) as overall_mastery FROM learner_profiles WHERE user_id = ?", (user_id,))
            overall_m = cursor.fetchone()["overall_mastery"] or 0.0

            return {
                "user_id": user_id,
                "total_sessions": tot_sess,
                "total_attempts": tot_att,
                "overall_mastery": round(overall_m, 2)
            }