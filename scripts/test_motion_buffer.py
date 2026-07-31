import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import time
from backend.app.ai.ml.inference.temporal_buffer import TemporalLandmarkBuffer
from backend.app.services.motion_assessment_engine import MotionAssessmentEngine

def test_pipeline():
    print("--- Testing Temporal Buffer ---")
    buffer = TemporalLandmarkBuffer(buffer_size=30, landmark_dim=63)
    
    # Simulate adding 35 frames (should auto-discard oldest 5)
    for i in range(35):
        dummy_vector = np.full(63, i, dtype=float)
        buffer.add_frame(dummy_vector)
        
    sequence = buffer.get_sequence()
    print(f"Buffer full status: {buffer.is_full()}")
    print(f"Sequence shape: {sequence.shape} (Expected: (30, 63))")
    print(f"Oldest frame retained start value: {sequence[0][0]} (Expected: 5.0)")

    print("\n--- Testing Motion Assessment Engine ---")
    engine = MotionAssessmentEngine(target_gesture="A")
    
    # Simulate 5 invalid frames
    for _ in range(5):
        engine.process_frame(np.zeros(63), prediction="B", confidence=0.4, is_valid=False)
        
    # Simulate 20 valid frames
    for _ in range(20):
        # Adding slight jitter to test stability
        jitter_vector = np.ones(63) + np.random.normal(0, 0.01, 63)
        engine.process_frame(jitter_vector, prediction="A", confidence=0.92, is_valid=True)
        time.sleep(0.02)
        
    report = engine.evaluate_performance()
    print("Assessment Report Output:")
    for key, value in report.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_pipeline()
    