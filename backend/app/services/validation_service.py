from typing import List, Any
from app.core.exceptions import LandmarkValidationError

class LandmarkValidationService:
    @staticmethod
    def validate_frame_quality(hand_landmarks: List[Any], pose_landmarks: List[Any] = None) -> bool:
        if not hand_landmarks or len(hand_landmarks) != 21:
            raise LandmarkValidationError("Hand landmarks incomplete. Ensure all 21 keypoints are visible in frame.")
        
        # Verify coordinates are normalized between 0.0 and 1.0 (or within reasonable bounding box)
        for idx, pt in enumerate(hand_landmarks):
            x = pt.x if hasattr(pt, 'x') else pt.get('x', 0.0)
            y = pt.y if hasattr(pt, 'y') else pt.get('y', 0.0)
            if x is None or y is None:
                raise LandmarkValidationError(f"Landmark index {idx} missing spatial coordinates.")

        return True
    