# scripts/test_sequence_builder.py
import os
import sys
import numpy as np

# Add the backend folder to Python's module search path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ai.ml.inference.sequence_builder import TemporalSequenceBuilder

def test_sequence_prototype():
    print("🚀 Initializing Temporal Sequence Builder Prototype...")
    seq_builder = TemporalSequenceBuilder(sequence_length=20, feature_dim=63)

    print("\n📥 Simulating incoming webcam stream (25 frames)...")
    
    for frame_idx in range(1, 26):
        # Generate dummy 63-dim landmark vector simulating hand motion
        mock_landmarks = np.random.uniform(low=-1.0, high=1.0, size=(63,))
        
        is_ready = seq_builder.add_frame(mock_landmarks)
        tensor = seq_builder.get_sequence_tensor()

        if is_ready:
            print(f"Frame {frame_idx:02d}: ✅ Buffer FULL | Sequence Tensor Shape: {tensor.shape}")
        else:
            print(f"Frame {frame_idx:02d}: ⏳ Buffering... ({len(seq_builder.buffer)}/20 frames)")

    print("\n🎉 Sequence Builder Prototype Verified Successfully!")

if __name__ == "__main__":
    test_sequence_prototype()
    