import time
from collections import deque
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple, Dict, Any
import numpy as np

# ==========================================
# DATA STRUCTURES
# ==========================================

@dataclass
class ValidationResult:
    is_valid: bool
    status_code: str
    feedback_message: Optional[str] = None

@dataclass
class AssessmentReport:
    timestamp: float
    expected_gesture: str
    predicted_gesture: str
    is_correct: bool
    confidence_score: float
    time_to_complete_sec: float
    unstable_frame_count: int
    gesture_stability_score: float  # 0.0 to 100.0
    overall_assessment_score: float # 0.0 to 100.0
    feedback_messages: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ==========================================
# 1. FRAME VALIDATION MODULE
# ==========================================

class FrameValidator:
    """Validates scene conditions before appending to temporal buffer."""
    
    @staticmethod
    def validate_frame(
        pose_landmarks, 
        hand_landmarks_list, 
        image_shape: Tuple[int, int]
    ) -> ValidationResult:

        # 1. Check for presence of person
        if not pose_landmarks:
            return ValidationResult(
                is_valid=False, 
                status_code="NO_PERSON", 
                feedback_message="Please stand in view of the camera."
            )

        # 2. Check for presence of hands
        if not hand_landmarks_list or len(hand_landmarks_list) == 0:
            return ValidationResult(
                is_valid=False, 
                status_code="NO_HANDS", 
                feedback_message="Keep your signing hand clearly visible."
            )

        # 3. Check upper body visibility (Shoulders at index 11 and 12)
        left_shoulder = pose_landmarks[11]
        right_shoulder = pose_landmarks[12]
        
        # Safely extract visibility if present (MediaPipe Tasks uses attributes)
        left_vis = getattr(left_shoulder, 'visibility', 1.0)
        right_vis = getattr(right_shoulder, 'visibility', 1.0)

        if left_vis < 0.5 or right_vis < 0.5:
            return ValidationResult(
                is_valid=False, 
                status_code="PARTIAL_BODY", 
                feedback_message="Please keep your upper body fully visible inside the camera frame."
            )

        # 4. Check hand positioning (Wrist at index 0)
        primary_hand = hand_landmarks_list[0]
        wrist = primary_hand[0]
        margin_x, margin_y = 0.08, 0.08
        if not (margin_x < wrist.x < 1 - margin_x and margin_y < wrist.y < 1 - margin_y):
            return ValidationResult(
                is_valid=False, 
                status_code="HAND_OFF_CENTER", 
                feedback_message="Move your hand closer to the center of the frame."
            )

        return ValidationResult(is_valid=True, status_code="OK")


# ==========================================
# 2. TEMPORAL BUFFER & STABILITY DETECTOR
# ==========================================

class TemporalBufferManager:
    """Maintains a rolling queue of landmark vectors."""
    
    def __init__(self, buffer_size: int = 30):
        self.buffer = deque(maxlen=buffer_size)

    def append(self, landmark_vector: np.ndarray):
        self.buffer.append(landmark_vector)

    def is_full(self) -> bool:
        return len(self.buffer) == self.buffer.maxlen


class GestureStabilizer:
    """Requires N consistent consecutive frame predictions to confirm a gesture."""
    
    def __init__(self, consistency_threshold: int = 5):
        self.threshold = consistency_threshold
        self.history = deque(maxlen=consistency_threshold)
        self.unstable_frames_count = 0

    def process_prediction(self, raw_prediction: str) -> Tuple[Optional[str], int]:
        self.history.append(raw_prediction)

        if len(self.history) < self.threshold:
            self.unstable_frames_count += 1
            return None, self.unstable_frames_count

        first_elem = self.history[0]
        if all(pred == first_elem for pred in self.history) and first_elem != "UNKNOWN":
            return first_elem, self.unstable_frames_count
        else:
            self.unstable_frames_count += 1
            return None, self.unstable_frames_count


# ==========================================
# 3. INTELLIGENT SIGN ASSESSMENT ENGINE
# ==========================================

class IntelligentAssessmentEngine:
    """Evaluates practice attempt and generates structured feedback."""
    
    def evaluate(
        self,
        expected_gesture: str,
        predicted_gesture: Optional[str],
        confidence: float,
        time_taken_sec: float,
        unstable_frames: int,
        total_frames_processed: int,
        validation_errors: List[str]
    ) -> AssessmentReport:
        
        is_correct = (predicted_gesture == expected_gesture)
        feedback = []

        # Stability Calculation
        stable_ratio = max(0.0, 1.0 - (unstable_frames / max(1, total_frames_processed)))
        gesture_stability_score = round(stable_ratio * 100, 2)

        # Rule-Based Feedback Layer
        if "HAND_OFF_CENTER" in validation_errors:
            feedback.append("Move your hand closer to the center of the frame.")

        if "PARTIAL_BODY" in validation_errors:
            feedback.append("Please keep your upper body fully visible inside the camera frame.")

        if "NO_HANDS" in validation_errors:
            feedback.append("Your hand dropped out of sight. Keep your signing hand clearly visible.")

        if unstable_frames > 12 and is_correct:
            feedback.append("Your hand moved before prediction stabilized. Hold steadier.")

        if confidence < 0.75 and is_correct:
            feedback.append("Hold the gesture slightly longer before releasing.")

        if not is_correct and predicted_gesture is not None:
            feedback.append(f"Form check: System detected '{predicted_gesture}' instead of '{expected_gesture}'.")

        if not feedback and is_correct:
            feedback.append("Excellent execution! Smooth stability and clear positioning.")

        # Composite Scoring (50% Accuracy + 30% Stability + 20% Confidence)
        accuracy_points = 50.0 if is_correct else 0.0
        stability_points = (gesture_stability_score / 100.0) * 30.0
        confidence_points = min(confidence, 1.0) * 20.0
        
        overall_score = round(accuracy_points + stability_points + confidence_points, 2)

        return AssessmentReport(
            timestamp=time.time(),
            expected_gesture=expected_gesture,
            predicted_gesture=predicted_gesture or "None",
            is_correct=is_correct,
            confidence_score=round(confidence, 4),
            time_to_complete_sec=round(time_taken_sec, 2),
            unstable_frame_count=unstable_frames,
            gesture_stability_score=gesture_stability_score,
            overall_assessment_score=overall_score,
            feedback_messages=feedback
        )


# ==========================================
# 4. PIPELINE ORCHESTRATOR
# ==========================================

class MockInferenceEngine:
    """Mock classifier. Replace with your actual model in production."""
    def predict(self, landmark_vector: np.ndarray) -> Tuple[str, float]:
        return "HELLO", 0.92


class RealTimeGesturePipeline:
    def __init__(self, expected_gesture: str = "HELLO"):
        self.expected_gesture = expected_gesture
        self.buffer = TemporalBufferManager(buffer_size=30)
        self.stabilizer = GestureStabilizer(consistency_threshold=6)
        self.validator = FrameValidator()
        self.model = MockInferenceEngine()
        self.assessment_engine = IntelligentAssessmentEngine()
        
        self.fps_queue = deque(maxlen=30)
        self.validation_errors_session = []
        self.start_time = time.time()
        self.total_frames = 0

    def process_frame(
        self, 
        frame: np.ndarray, 
        pose_landmarks, 
        hand_landmarks_list
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()
        self.total_frames += 1

        # 1. Validate Frame
        val_result = self.validator.validate_frame(pose_landmarks, hand_landmarks_list, frame.shape)
        
        if not val_result.is_valid:
            self.validation_errors_session.append(val_result.status_code)
            return {
                "status": "INVALID_FRAME",
                "message": val_result.feedback_message,
                "metrics": {"fps": self._calc_fps(t0), "latency_ms": (time.perf_counter() - t0) * 1000}
            }

        # 2. Extract Landmarks (21 joints x 3 coords = 63 floats)
        primary_hand = hand_landmarks_list[0]
        landmarks_vector = np.array([[lm.x, lm.y, lm.z] for lm in primary_hand]).flatten()

        # 3. Buffer Vector
        self.buffer.append(landmarks_vector)

        # 4. Inference
        raw_pred, raw_conf = self.model.predict(landmarks_vector)

        # 5. Stability Filter
        confirmed_gesture, unstable_count = self.stabilizer.process_prediction(raw_pred)

        latency_ms = (time.perf_counter() - t0) * 1000
        current_fps = self._calc_fps(t0)

        # 6. Generate Assessment on confirmed gesture
        assessment_data = None
        if confirmed_gesture:
            time_taken = time.time() - self.start_time
            assessment = self.assessment_engine.evaluate(
                expected_gesture=self.expected_gesture,
                predicted_gesture=confirmed_gesture,
                confidence=raw_conf,
                time_taken_sec=time_taken,
                unstable_frames=unstable_count,
                total_frames_processed=self.total_frames,
                validation_errors=self.validation_errors_session
            )
            assessment_data = assessment.to_dict()

        return {
            "status": "PROCESSING",
            "raw_prediction": raw_pred,
            "confirmed_gesture": confirmed_gesture,
            "confidence": raw_conf,
            "metrics": {
                "latency_ms": round(latency_ms, 2),
                "fps": round(current_fps, 1),
            },
            "assessment": assessment_data
        }

    def _calc_fps(self, t0: float) -> float:
        elapsed = time.perf_counter() - t0
        self.fps_queue.append(1.0 / max(elapsed, 0.0001))
        return float(np.mean(self.fps_queue))
    