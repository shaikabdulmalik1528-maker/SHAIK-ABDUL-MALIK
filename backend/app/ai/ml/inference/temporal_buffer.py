from collections import deque
import numpy as np


class TemporalLandmarkBuffer:
    def __init__(self, buffer_size: int = 30, landmark_dim: int = 63):
        """Initializes a fixed-size FIFO landmark queue.

        :param buffer_size: Number of temporal frames to keep (20-30).
        :param landmark_dim: Dimensionality of flattened landmarks (e.g., 21
            points * 3 coordinates = 63).
        """
        self.buffer_size = buffer_size
        self.landmark_dim = landmark_dim
        self.buffer = deque(maxlen=buffer_size)

    def add_frame(self, landmark_vector: np.ndarray):
        """Appends a frame vector to the buffer.

        Automatically purges oldest frame when full.
        """
        if landmark_vector is None or len(landmark_vector) != self.landmark_dim:
            landmark_vector = np.zeros(self.landmark_dim)

        self.buffer.append(landmark_vector)

    def get_sequence(self) -> np.ndarray:
        """Exposes the full sequence array (Shape: [frames, features])."""
        return np.array(self.buffer)

    def is_full(self) -> bool:
        return len(self.buffer) == self.buffer_size

    def clear(self):
        self.buffer.clear()
        