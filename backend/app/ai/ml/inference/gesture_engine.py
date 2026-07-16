import os
import time
import logging
from typing import Optional, Tuple
import numpy as np
import cv2
import mediapipe as mp
import joblib
from pydantic import BaseModel

# Configure logger for tracking inference metadata
logger = logging.getLogger("AIEngine")
logger.setLevel(logging.INFO)


class PredictionResult(BaseModel):
    """Enforced structured prediction schema for API outputs."""
    gesture: str
    confidence: float
    model_version: str
    inference_time_ms: float
    hand_detected: bool
    landmarks_validated: bool


class GestureEngine:
    """
    Production-Ready self-contained AI module.
    Encapsulates raw image preprocessing, MediaPipe hand tracking, 
    landmark normalization, and model inference.
    """
    def __init__(
        self, 
        model_path: str, 
        model_version: str = "rf_v1.0", 
        confidence_threshold: float = 0.70
    ):
        self.model_version = model_version
        self.confidence_threshold = confidence_threshold
        
        # Load Model
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model checkpoint not found at: {model_path}")
        self.model = joblib.load(model_path)
        logger.info(f"Model {self.model_version} successfully loaded.")

        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        logger.info("MediaPipe hand tracking initialized.")

    def _extract_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Runs MediaPipe to extract raw 21 hand landmarks (X, Y, Z)."""
        # Convert BGR (OpenCV standard) to RGB (MediaPipe requirement)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        if not results.multi_hand_landmarks:
            return None
            
        # Extract landmarks for the first hand detected
        hand_landmarks = results.multi_hand_landmarks[0]
        return np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])

    def _validate_features(self, landmarks: np.ndarray) -> bool:
        """Validates features to prevent downstream math or model crashes."""
        if landmarks.shape != (21, 3):
            return False
        if np.isnan(landmarks).any() or np.isinf(landmarks).any():
            return False
        return True

    def _normalize_features(self, landmarks: np.ndarray) -> np.ndarray:
        """
        Translates and scales raw coordinates to achieve location and size invariance.
        Let $P_i = (x_i, y_i, z_i)$ represent landmark $i$, where $P_0$ is the wrist.
        """
        # 1. Wrist translation: Move coordinates relative to wrist (index 0)
        wrist = landmarks[0]
        translated = landmarks - wrist
        
        # 2. Hand-size scaling: Normalize by maximum distance from the wrist
        distances = np.linalg.norm(translated, axis=1)
        max_distance = np.max(distances)
        
        if max_distance == 0:
            return translated.flatten()
            
        normalized = translated / max_distance
        return normalized.flatten()  # 63-dimensional feature vector

    def predict(self, image: np.ndarray) -> PredictionResult:
        """
        Main exposed interface for backend developers.
        Accepts raw image array, runs full workflow, and returns structured metadata.
        """
        start_time = time.perf_counter()

        # 1. Landmark Extraction
        try:
            landmarks = self._extract_landmarks(image)
        except Exception as e:
            logger.error(f"MediaPipe processing error: {str(e)}")
            return self._build_fallback(time.perf_counter() - start_time, error_state="PIPELINE_ERROR")

        if landmarks is None:
            return self._build_fallback(time.perf_counter() - start_time, error_state="NO_HAND_DETECTED")

        # 2. Feature Validation
        if not self._validate_features(landmarks):
            return self._build_fallback(time.perf_counter() - start_time, error_state="INVALID_LANDMARKS", hand_detected=True)

        # 3. Feature Normalization (Shape: 1 x 63)
        features = self._normalize_features(landmarks).reshape(1, -1)

        # 4. Model Prediction & Confidence Thresholding
        try:
            probabilities = self.model.predict_proba(features)[0]
            max_idx = np.argmax(probabilities)
            confidence = float(probabilities[max_idx])

            if confidence >= self.confidence_threshold:
                predicted_gesture = str(self.model.classes_[max_idx])
            else:
                predicted_gesture = "UNKNOWN_LOW_CONFIDENCE"
        except Exception as e:
            logger.error(f"Inference execution failure: {str(e)}")
            return self._build_fallback(time.perf_counter() - start_time, error_state="INFERENCE_FAILED", hand_detected=True)

        inference_time_ms = (time.perf_counter() - start_time) * 1000

        # Log inference metadata
        logger.info(
            f"[INFERENCE] model={self.model_version} "
            f"gesture={predicted_gesture} confidence={confidence:.4f} "
            f"latency={inference_time_ms:.2f}ms"
        )

        return PredictionResult(
            gesture=predicted_gesture,
            confidence=confidence,
            model_version=self.model_version,
            inference_time_ms=inference_time_ms,
            hand_detected=True,
            landmarks_validated=True
        )

    def _build_fallback(self, elapsed_time_sec: float, error_state: str, hand_detected: bool = False) -> PredictionResult:
        """Helper to safely build schema-conforming error outputs."""
        return PredictionResult(
            gesture=error_state,
            confidence=0.0,
            model_version=self.model_version,
            inference_time_ms=elapsed_time_sec * 1000,
            hand_detected=hand_detected,
            landmarks_validated=False
        )
        