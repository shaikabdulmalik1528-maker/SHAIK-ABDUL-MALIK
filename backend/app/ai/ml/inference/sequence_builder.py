# backend/app/ai/ml/inference/sequence_builder.py
import numpy as np
from collections import deque
from typing import Optional, Tuple


class TemporalSequenceBuilder:
    """
    Manages a sliding-window temporal buffer to aggregate 63-dimensional
    landmark vectors across consecutive frames for sequence models (LSTM/GRU).
    """

    def __init__(self, sequence_length: int = 20, feature_dim: int = 63):
        """
        Args:
            sequence_length (int): Number of consecutive frames (N) to store.
            feature_dim (int): Number of landmark features per frame (21 keypoints * 3D = 63).
        """
        self.sequence_length = sequence_length
        self.feature_dim = feature_dim
        # Using a fixed-size deque acts as an automatic sliding window
        self.buffer = deque(maxlen=sequence_length)

    def add_frame(self, landmark_vector: Optional[np.ndarray]) -> bool:
        """
        Adds a single frame's 63-dim feature vector to the buffer.
        If no hand is detected (None), pads with zeros to maintain temporal continuity.
        
        Returns:
            bool: True if the sequence buffer is full and ready for inference, False otherwise.
        """
        if landmark_vector is None:
            # Zero-padding fallback for missing hands in continuous streams
            vector_to_add = np.zeros(self.feature_dim, dtype=np.float32)
        else:
            vector_to_add = np.asarray(landmark_vector, dtype=np.float32).flatten()
            
            if vector_to_add.shape[0] != self.feature_dim:
                raise ValueError(
                    f"Expected feature vector of length {self.feature_dim}, got {vector_to_add.shape[0]}"
                )

        self.buffer.append(vector_to_add)
        return len(self.buffer) == self.sequence_length

    def get_sequence_tensor(self) -> Optional[np.ndarray]:
        """
        Converts the current frame buffer into a sequence tensor ready for model input.
        
        Returns:
            np.ndarray: Shape (1, sequence_length, feature_dim) -> (1, 20, 63)
            Returns None if the buffer is not yet full.
        """
        if len(self.buffer) < self.sequence_length:
            return None

        # Convert deque to array -> shape: (20, 63)
        sequence_matrix = np.array(self.buffer, dtype=np.float32)

        # Expand dimensions to add batch size -> shape: (1, 20, 63)
        sequence_tensor = np.expand_dims(sequence_matrix, axis=0)
        return sequence_tensor

    def reset(self):
        """Clears the temporal buffer (e.g., when a user stops signing)."""
        self.buffer.clear()