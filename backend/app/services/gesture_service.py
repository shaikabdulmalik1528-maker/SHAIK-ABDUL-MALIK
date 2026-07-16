# backend/app/services/gesture_service.py
import os
import numpy as np
from app.ai.ml.inference.gesture_engine import GestureEngine, PredictionResult

class GestureService:
    def __init__(self):
        # 1. Locate this file's current directory:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Travel up 3 levels to the root directory (SignLanguagePlatform)
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        
        # 3. Target your actual pickle model file
        model_path = os.path.join(project_root, "models", "random_forest_model.pkl")
        
        print(f"🔍 [DEBUG] Resolved absolute model path: {model_path}")
        
        # 4. Initialize the production engine with the correct path
        self.engine = GestureEngine(model_path=model_path, model_version="rf_v1.0")

    def predict_image(self, image: np.ndarray) -> PredictionResult:
        return self.engine.predict(image)
    