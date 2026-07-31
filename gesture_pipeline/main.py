import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import json
from pipeline import RealTimeGesturePipeline

def run_webcam():
    # 1. Initialize Hand Landmarker Task
    hand_base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    hand_options = vision.HandLandmarkerOptions(
        base_options=hand_base_options,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5
    )
    hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)

    # 2. Initialize Pose Landmarker Task
    pose_base_options = python.BaseOptions(model_asset_path='pose_landmarker.task')
    pose_options = vision.PoseLandmarkerOptions(
        base_options=pose_base_options,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5
    )
    pose_landmarker = vision.PoseLandmarker.create_from_options(pose_options)

    # Initialize Gesture Pipeline
    pipeline = RealTimeGesturePipeline(expected_gesture="HELLO")

    # Start Webcam Stream
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Starting pipeline... Press 'q' to quit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert OpenCV Frame to MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run Detectors
        hand_results = hand_landmarker.detect(mp_image)
        pose_results = pose_landmarker.detect(mp_image)

        # Format landmarks for pipeline compatibility
        pose_landmarks = pose_results.pose_landmarks[0] if pose_results.pose_landmarks else None
        hand_landmarks_list = hand_results.hand_landmarks if hand_results.hand_landmarks else None

        # Process through pipeline
        output = pipeline.process_frame(frame, pose_landmarks, hand_landmarks_list)

        # --- ONSCREEN DISPLAY (HUD) ---
        status = output.get("status")
        metrics = output.get("metrics", {})
        fps = metrics.get("fps", 0)
        latency = metrics.get("latency_ms", 0)

        cv2.putText(frame, f"FPS: {fps} | Latency: {latency:.1f}ms", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if status == "INVALID_FRAME":
            msg = output.get("message", "Invalid Frame")
            cv2.putText(frame, f"STATUS: {msg}", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        elif status == "PROCESSING":
            raw_pred = output.get("raw_prediction")
            confirmed = output.get("confirmed_gesture")
            conf = output.get("confidence", 0)

            cv2.putText(frame, f"Raw Pred: {raw_pred} ({conf:.2f})", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            if confirmed:
                cv2.putText(frame, f"STABLE GESTURE: {confirmed}", (20, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 3)

            assessment = output.get("assessment")
            if assessment:
                print("\n================ ASSESSMENT REPORT ================")
                print(json.dumps(assessment, indent=2))
                print("===================================================\n")

        cv2.imshow("Real-Time Gesture Pipeline & Assessment", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    hand_landmarker.close()
    pose_landmarker.close()

if __name__ == "__main__":
    run_webcam()