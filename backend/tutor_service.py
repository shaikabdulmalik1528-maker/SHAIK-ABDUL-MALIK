import sqlite3
import uuid
import time
import string
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from error_analysis import ErrorAnalysisModule
except ImportError:
    # Fallback dummy class if error_analysis module is not fully loaded
    class ErrorAnalysisModule:
        def __init__(self, db_path: str): pass
        def analyze_user_performance(self, user_id: str): return {"insights": {}}

class IntelligentTutorService:
    """
    Extends assessment workflow: evaluates historical performance, 
    generates actionable personalized feedback, updates learner profile metrics,
    and returns dynamic practice recommendations with rationale.
    """
    def __init__(self, db_path: str = "app_data.db"):
        self.db_path = db_path
        self.analyzer = ErrorAnalysisModule(db_path=self.db_path)

        # Domain knowledge: Physical guidance tips for common mix-ups
        self.physical_corrections = {
            ("M", "N"): "For 'M', tuck your thumb under three fingers. For 'N', tuck it under only two fingers.",
            ("A", "S"): "For 'A', place your thumb along the side of your fist. For 'S', cross your thumb over the front of your fingers.",
            ("K", "V"): "For 'K', place your thumb between your index and middle finger. For 'V', make a clear 'V' without thumb contact.",
            ("E", "O"): "For 'E', curl your finger tips down onto your thumb top. For 'O', form a round circle.",
        }

        # Initialize full profile table schema
        self._init_extended_db()

    def _get_connection(self):
        # timeout=10.0 prevents 'database is locked' errors
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_extended_db(self):
        """Creates tables for attempts, learner profiles, and confusion matrix."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Unified practice_attempts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS practice_attempts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_id TEXT,
                    target_alphabet TEXT,
                    predicted_alphabet TEXT,
                    confidence_score REAL,
                    is_correct INTEGER,
                    timestamp REAL
                )
            """)

            # Learner Profile Table (Tracks attempts, streaks, confidence EMA, last practiced)
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

            # Confusion Matrix Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS confusion_matrix (
                    user_id TEXT,
                    expected_alphabet TEXT,
                    predicted_alphabet TEXT,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, expected_alphabet, predicted_alphabet)
                )
            """)

            # Feedback History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assessment_feedback_history (
                    id TEXT PRIMARY KEY,
                    attempt_id TEXT,
                    feedback_type TEXT,
                    title TEXT,
                    message TEXT,
                    action_item TEXT
                )
            """)
            conn.commit()

    def _ensure_profile_exists(self, user_id: str, conn: sqlite3.Connection):
        """Ensures all 26 alphabets (A-Z) are initialized for the user profile."""
        cursor = conn.cursor()
        for char in string.ascii_uppercase:
            cursor.execute("""
                INSERT OR IGNORE INTO learner_profiles (user_id, alphabet)
                VALUES (?, ?)
            """, (user_id, char))

    def process_prediction_event(
        self, user_id: str, session_id: str, target: str, predicted: str, confidence: float
    ) -> Dict[str, Any]:
        """Core workflow execution using a single connection to avoid SQLite locks."""
        target = target.upper()
        predicted = predicted.upper()
        is_correct = (target == predicted)
        attempt_id = str(uuid.uuid4())
        now_epoch = time.time()

        with self._get_connection() as conn:
            self._ensure_profile_exists(user_id, conn)

            # 1. Retrieve historical analytics safely
            try:
                analysis = self.analyzer.analyze_user_performance(user_id)
            except Exception:
                analysis = {"insights": {}}

            # 2. Generate personalized feedback
            feedback = self._generate_personalized_feedback(
                target=target,
                predicted=predicted,
                confidence=confidence,
                analysis=analysis
            )

            # 3. Update Learner Profile & Compute Mastery State
            updated_state = self._update_and_compute_profile(
                conn=conn,
                user_id=user_id,
                target=target,
                predicted=predicted,
                confidence=confidence,
                is_correct=is_correct,
                now_epoch=now_epoch,
                analysis=analysis
            )

            # 4. Save attempt and feedback atomically into SQLite
            self._persist_assessment(
                conn=conn,
                attempt_id=attempt_id,
                user_id=user_id,
                session_id=session_id,
                target=target,
                predicted=predicted,
                confidence=confidence,
                is_correct=is_correct,
                feedback=feedback,
                now_epoch=now_epoch
            )

            conn.commit()

        # 5. Generate Personalized Recommendations Queue
        recommendations = self.generate_recommendations(user_id=user_id)

        return {
            "attempt_id": attempt_id,
            "prediction_result": {
                "target": target,
                "predicted": predicted,
                "confidence": round(confidence, 4),
                "is_correct": is_correct
            },
            "feedback": feedback,
            "updated_learning_state": updated_state,
            "next_recommendations": recommendations
        }

    def _generate_personalized_feedback(
        self, target: str, predicted: str, confidence: float, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        is_correct = (target == predicted)
        insights = analysis.get("insights", {}) if analysis else {}
        repeated_mistakes = [r["alphabet"] for r in insights.get("repeated_mistakes", [])]

        if is_correct:
            if target in repeated_mistakes:
                return {
                    "type": "BREAKTHROUGH",
                    "title": f"Great Job! Breakthrough on '{target}'",
                    "message": f"You previously struggled with '{target}' across multiple sessions. You nailed it this time!",
                    "action_item": "Repeat it 2 more times right now to lock in the muscle memory."
                }
            elif confidence < 0.65:
                return {
                    "type": "UNCERTAIN_CORRECT",
                    "title": "Correct, but hand posture is loose",
                    "message": f"Recognized '{target}', but low confidence ({round(confidence * 100)}%) indicates fingers are slightly misaligned.",
                    "action_item": "Hold your hand firmer and align your fingers strictly toward the camera."
                }
            else:
                return {
                    "type": "SUCCESS",
                    "title": "Clean execution!",
                    "message": f"Perfect sign for letter '{target}'.",
                    "action_item": "Move on to the next alphabet."
                }

        confused_pairs = insights.get("frequently_confused_pairs", [])
        is_known_confusion = any(
            p["target"] == target and p["confused_with"] == predicted for p in confused_pairs
        )

        if is_known_confusion:
            tip = self.physical_corrections.get(
                (target, predicted), 
                f"Pay close attention to finger and thumb positions between '{target}' and '{predicted}'."
            )
            return {
                "type": "REPEATED_CONFUSION",
                "title": f"Common Mix-Up: '{target}' vs '{predicted}'",
                "message": f"You frequently sign '{predicted}' when aiming for '{target}'. {tip}",
                "action_item": f"Adjustment Tip: {tip}"
            }

        tip = self.physical_corrections.get(
            (target, predicted), 
            f"Check finger arrangement for '{target}' compared to '{predicted}'."
        )
        return {
            "type": "MISCLASSIFICATION",
            "title": f"Incorrect Gesture for '{target}'",
            "message": f"You intended '{target}', but the model detected '{predicted}'.",
            "action_item": f"Quick fix: {tip}"
        }

    def _update_and_compute_profile(
        self, conn: sqlite3.Connection, user_id: str, target: str, predicted: str, 
        confidence: float, is_correct: bool, now_epoch: float, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM learner_profiles WHERE user_id = ? AND alphabet = ?", (user_id, target))
        row = cursor.fetchone()

        tot_attempts = (row["total_attempts"] if row else 0) + 1
        tot_correct = (row["total_correct"] if row else 0) + (1 if is_correct else 0)
        cons_correct = ((row["consecutive_correct"] if row else 0) + 1) if is_correct else 0
        cons_incorrect = ((row["consecutive_incorrect"] if row else 0) + 1) if not is_correct else 0

        alpha = 0.3
        prev_avg_conf = (row["avg_confidence"] if row else 0.0) or 0.0
        new_avg_conf = confidence if tot_attempts == 1 else ((1 - alpha) * prev_avg_conf + (alpha * confidence))

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

        revisions = analysis.get("insights", {}).get("gestures_requiring_immediate_revision", []) if analysis else []
        mastery_label = "NEEDS_REVISION" if (target in revisions and not is_correct) else ("MASTERED" if is_correct else "PRACTICING")

        return {
            "target_alphabet": target,
            "mastery_score": round(mastery_score, 2),
            "mastery_level": mastery_label,
            "total_attempts": tot_attempts,
            "consecutive_correct": cons_correct,
            "consecutive_incorrect": cons_incorrect,
            "avg_confidence": round(new_avg_conf, 2),
            "priority_revision_queue": revisions
        }

    def _persist_assessment(
        self, conn: sqlite3.Connection, attempt_id: str, user_id: str, session_id: str, 
        target: str, predicted: str, confidence: float, is_correct: bool, 
        feedback: Dict[str, Any], now_epoch: float
    ):
        cursor = conn.cursor()

        # Save prediction attempt into practice_attempts
        cursor.execute(
            """
            INSERT INTO practice_attempts 
            (id, user_id, session_id, target_alphabet, predicted_alphabet, confidence_score, is_correct, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (attempt_id, user_id, session_id, target, predicted, confidence, 1 if is_correct else 0, now_epoch)
        )

        # Save generated feedback record
        cursor.execute(
            """
            INSERT INTO assessment_feedback_history
            (id, attempt_id, feedback_type, title, message, action_item)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()), attempt_id, feedback["type"], 
                feedback["title"], feedback["message"], feedback["action_item"]
            )
        )

    def generate_recommendations(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Analyzes practice history to rank the next alphabets to practice with rationales."""
        recommendations = []
        now = time.time()
        DAY_IN_SEC = 86400

        with self._get_connection() as conn:
            self._ensure_profile_exists(user_id, conn)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM learner_profiles WHERE user_id = ?", (user_id,))
            profiles = cursor.fetchall()

            for p in profiles:
                alph = p["alphabet"]
                mastery = p["mastery_level"]
                last_time = p["last_practiced_at"]
                avg_conf = p["avg_confidence"]
                cons_corr = p["consecutive_correct"]

                priority_score = 0.0
                reason_cat = "LOW_MASTERY"
                rationale = f"Low mastery level ({int(mastery * 100)}%)."

                if not last_time:
                    priority_score = 50.0
                    reason_cat = "NOT_PRACTICED_RECENTLY"
                    rationale = "Has not been practiced yet."
                else:
                    priority_score += (1.0 - mastery) * 40.0

                    days_ago = (now - last_time) / DAY_IN_SEC
                    if days_ago >= 1.0:
                        decay_score = min(days_ago * 10.0, 30.0)
                        priority_score += decay_score
                        if decay_score > ((1.0 - mastery) * 40.0):
                            reason_cat = "NOT_PRACTICED_RECENTLY"
                            rationale = f"Not practiced in {int(days_ago)} day(s)."

                    cursor.execute("""
                        SELECT predicted_alphabet, count FROM confusion_matrix 
                        WHERE user_id = ? AND expected_alphabet = ? 
                        ORDER BY count DESC LIMIT 1
                    """, (user_id, alph))
                    conf_row = cursor.fetchone()
                    if conf_row and conf_row["count"] >= 2:
                        priority_score += 25.0
                        reason_cat = "FREQUENT_CONFUSION"
                        rationale = f"Frequently confused with '{conf_row['predicted_alphabet']}'."

                    if mastery >= 0.5 and avg_conf < 0.65:
                        priority_score += 20.0
                        reason_cat = "LOW_CONFIDENCE"
                        rationale = f"Low confidence ({int(avg_conf * 100)}%) despite correct predictions."

                    if cons_corr >= 3 and mastery >= 0.8:
                        priority_score += 15.0
                        reason_cat = "READY_TO_PROGRESS"
                        rationale = f"High improvement trend ({cons_corr} streak). Ready to progress!"

                recommendations.append({
                    "alphabet": alph,
                    "priority_score": round(priority_score, 2),
                    "reason_category": reason_cat,
                    "rationale": rationale
                })

        recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
        return recommendations[:limit]

    def get_analytics_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Returns overview metrics for dynamic dashboard refreshes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total_attempts FROM practice_attempts WHERE user_id = ?", (user_id,))
            row_att = cursor.fetchone()
            total_attempts = row_att["total_attempts"] if row_att else 0

            cursor.execute("SELECT COUNT(DISTINCT session_id) as total_sessions FROM practice_attempts WHERE user_id = ?", (user_id,))
            row_sess = cursor.fetchone()
            total_sessions = row_sess["total_sessions"] if row_sess else 0

            cursor.execute("SELECT AVG(mastery_level) as overall_mastery FROM learner_profiles WHERE user_id = ?", (user_id,))
            row_m = cursor.fetchone()
            overall_mastery = (row_m["overall_mastery"] if row_m and row_m["overall_mastery"] is not None else 0.0)

            cursor.execute("SELECT * FROM learner_profiles WHERE user_id = ?", (user_id,))
            profiles = [dict(row) for row in cursor.fetchall()]

            return {
                "user_id": user_id,
                "total_sessions": total_sessions,
                "total_attempts": total_attempts,
                "overall_mastery": round(overall_mastery, 2),
                "alphabet_profiles": profiles
            }
            