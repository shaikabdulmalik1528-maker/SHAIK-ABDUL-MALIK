import sqlite3
from datetime import datetime
from typing import Dict, List, Any

class ErrorAnalysisModule:
    """
    Backend service that analyzes stored practice attempts 
    and generates meaningful learning insights as JSON.
    """
    def __init__(self, db_path: str = "app_data.db", low_confidence_threshold: float = 0.65):
        self.db_path = db_path
        self.low_confidence_threshold = low_confidence_threshold

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Returns rows as dictionary-like objects
        return conn

    def analyze_user_performance(self, user_id: str) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()

        # Fetch all historical attempts for the user
        cursor.execute(
            """
            SELECT target_alphabet, predicted_alphabet, confidence_score, is_correct, session_id, created_at
            FROM prediction_attempts
            WHERE user_id = ?
            ORDER BY created_at ASC
            """,
            (user_id,)
        )
        attempts = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not attempts:
            return self._empty_response()

        # 1. Most Frequently Confused Pairs (e.g., M -> N)
        confused_pairs = self._get_confused_pairs(attempts)

        # 2. Alphabets with Consistently Low Confidence
        low_conf_alphabets = self._get_low_confidence_alphabets(attempts)

        # 3. Repeated Mistakes Across Multiple Sessions
        repeated_mistakes = self._get_repeated_mistakes(attempts)

        # 4. Gestures Requiring Immediate Revision
        immediate_revision = self._get_revision_priorities(attempts, repeated_mistakes)

        # 5. Improvement or Decline Performance Trends
        trends = self._get_performance_trends(attempts)

        total_attempts = len(attempts)
        overall_acc = sum(1 for a in attempts if a['is_correct']) / total_attempts if total_attempts > 0 else 0

        return {
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_attempts_analyzed": total_attempts,
            "overall_accuracy": round(overall_acc, 4),
            "insights": {
                "frequently_confused_pairs": confused_pairs,
                "low_confidence_alphabets": low_conf_alphabets,
                "repeated_mistakes": repeated_mistakes,
                "gestures_requiring_immediate_revision": immediate_revision,
                "alphabet_trends": trends
            }
        }

    def _get_confused_pairs(self, attempts: List[Dict]) -> List[Dict]:
        counts = {}
        for a in attempts:
            if not a['is_correct']:
                pair = (a['target_alphabet'], a['predicted_alphabet'])
                counts[pair] = counts.get(pair, 0) + 1

        sorted_pairs = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"target": target, "confused_with": predicted, "frequency": freq}
            for (target, predicted), freq in sorted_pairs[:5]
        ]

    def _get_low_confidence_alphabets(self, attempts: List[Dict]) -> List[Dict]:
        stats = {}
        for a in attempts:
            t = a['target_alphabet']
            if t not in stats:
                stats[t] = []
            stats[t].append(a['confidence_score'])

        low_conf = []
        for alphabet, scores in stats.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < self.low_confidence_threshold and len(scores) >= 3:
                low_conf.append({
                    "alphabet": alphabet,
                    "avg_confidence": round(avg_score, 4),
                    "total_attempts": len(scores)
                })
        return sorted(low_conf, key=lambda x: x['avg_confidence'])

    def _get_repeated_mistakes(self, attempts: List[Dict]) -> List[Dict]:
        session_failures = {}
        for a in attempts:
            if not a['is_correct']:
                target = a['target_alphabet']
                session = a['session_id']
                if target not in session_failures:
                    session_failures[target] = set()
                session_failures[target].add(session)

        repeated = [
            {"alphabet": target, "distinct_sessions_failed": len(sessions)}
            for target, sessions in session_failures.items()
            if len(sessions) >= 2
        ]
        return sorted(repeated, key=lambda x: x['distinct_sessions_failed'], reverse=True)

    def _get_revision_priorities(self, attempts: List[Dict], repeated: List[Dict]) -> List[str]:
        revision_set = set(r['alphabet'] for r in repeated)

        # Also add any gesture where accuracy in last 5 attempts is < 50%
        history_by_target = {}
        for a in attempts:
            target = a['target_alphabet']
            if target not in history_by_target:
                history_by_target[target] = []
            history_by_target[target].append(a['is_correct'])

        for target, correctness in history_by_target.items():
            recent = correctness[-5:]
            if len(recent) >= 2 and (sum(recent) / len(recent)) < 0.5:
                revision_set.add(target)

        return sorted(list(revision_set))

    def _get_performance_trends(self, attempts: List[Dict]) -> Dict[str, Dict]:
        history_by_target = {}
        for a in attempts:
            t = a['target_alphabet']
            if t not in history_by_target:
                history_by_target[t] = []
            history_by_target[t].append(a['is_correct'])

        trends = {}
        for target, results in history_by_target.items():
            if len(results) < 4:
                trends[target] = {"status": "INSUFFICIENT_DATA", "accuracy_change": 0.0}
                continue

            mid = len(results) // 2
            earlier_acc = sum(results[:mid]) / len(results[:mid])
            recent_acc = sum(results[mid:]) / len(results[mid:])
            delta = round(recent_acc - earlier_acc, 4)

            if delta >= 0.2:
                status = "IMPROVING"
            elif delta <= -0.2:
                status = "DECLINING"
            else:
                status = "STABLE"

            trends[target] = {
                "status": status,
                "accuracy_change": delta,
                "recent_accuracy": round(recent_acc, 4)
            }
        return trends

    def _empty_response(self) -> Dict[str, Any]:
        return {
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_attempts_analyzed": 0,
            "overall_accuracy": 0.0,
            "insights": {
                "frequently_confused_pairs": [],
                "low_confidence_alphabets": [],
                "repeated_mistakes": [],
                "gestures_requiring_immediate_revision": [],
                "alphabet_trends": {}
            }
        }
        