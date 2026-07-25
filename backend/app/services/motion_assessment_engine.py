import time
from typing import Any, Dict, List
import numpy as np


class MotionAssessmentEngine:
    def __init__(self, target_gesture: str):
        self.target_gesture = target_gesture
        self.reset()

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.landmark_history: List[np.ndarray] = []
        self.confidence_history: List[float] = []
        self.invalid_frame_count: int = 0
        self.valid_frame_count: int = 0

    def process_frame(
        self,
        landmark_vector: np.ndarray,
        prediction: str,
        confidence: float,
        is_valid: bool,
    ):
        if not is_valid or prediction != self.target_gesture:
            self.invalid_frame_count += 1
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.valid_frame_count += 1
        self.end_time = time.time()
        self.landmark_history.append(landmark_vector)
        self.confidence_history.append(confidence)

    def calculate_stability(self) -> float:
        if len(self.landmark_history) < 2:
            return 0.0

        sequence = np.array(self.landmark_history)
        coordinate_std = np.std(sequence, axis=0)
        mean_jitter = np.mean(coordinate_std)
        stability_score = max(0.0, 1.0 - (mean_jitter * 10.0))
        return float(stability_score)

    def evaluate_performance(self) -> Dict[str, Any]:
        if (
            self.start_time is None
            or self.end_time is None
            or not self.confidence_history
        ):
            return {"status": "FAILED", "reason": "Insufficient valid frames"}

        duration = self.end_time - self.start_time
        stability = self.calculate_stability()
        mean_confidence = float(np.mean(self.confidence_history))

        total_frames = self.valid_frame_count + self.invalid_frame_count
        shape_accuracy = self.valid_frame_count / max(1, total_frames)
        timing_score = max(0.0, 1.0 - (duration / 5.0))

        overall_score = (
            (0.40 * shape_accuracy)
            + (0.30 * mean_confidence)
            + (0.20 * stability)
            + (0.10 * timing_score)
        ) * 100.0

        return {
            "overall_score": round(overall_score, 2),
            "duration_seconds": round(duration, 2),
            "stability_score": round(stability * 100.0, 2),
            "invalid_frames_before_valid": self.invalid_frame_count,
            "mean_confidence": round(mean_confidence * 100.0, 2),
            "shape_accuracy": round(shape_accuracy * 100.0, 2),
        }
        