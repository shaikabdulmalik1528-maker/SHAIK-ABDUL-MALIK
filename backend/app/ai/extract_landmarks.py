import os
import cv2
import mediapipe as mp

# -------------------------------
# Initialize MediaPipe Hands
# -------------------------------
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)


# -------------------------------
# Extract landmarks from one image
# -------------------------------
def extract_landmarks(image_path):
    """
    Extract 21 hand landmarks (63 values) from a single image.

    Args:
        image_path (str): Path to image.

    Returns:
        list: 63 landmark values
        None: If image cannot be processed
    """

    image = cv2.imread(image_path)

    if image is None:
        return None

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_image)

    if not results.multi_hand_landmarks:
        return None

    hand_landmarks = results.multi_hand_landmarks[0]

    landmarks = []

    for landmark in hand_landmarks.landmark:
        landmarks.extend([
            landmark.x,
            landmark.y,
            landmark.z
        ])

    return landmarks


# -------------------------------
# Process the complete dataset
# -------------------------------
def process_dataset(dataset_path):

    dataset = []

    statistics = {
        "total_images": 0,
        "successful": 0,
        "failed": 0,
        "corrupted": 0
    }

    # -------------------------------
    # Validation Mode
    # Process only class A first
    # -------------------------------
    labels = os.listdir(dataset_path)

    # For full dataset later, replace the above line with:
    # labels = os.listdir(dataset_path)

    for label in labels:

        class_path = os.path.join(dataset_path, label)

        if not os.path.isdir(class_path):
            print(f"Class folder not found: {class_path}")
            continue

        print(f"\nProcessing class: {label}")

        for image_name in os.listdir(class_path):

            image_path = os.path.join(class_path, image_name)

            statistics["total_images"] += 1

            if statistics["total_images"] % 100 == 0:
                print(f"Processed {statistics['total_images']} images...")

            image = cv2.imread(image_path)

            if image is None:
                statistics["corrupted"] += 1
                continue

            landmarks = extract_landmarks(image_path)

            if landmarks is None:
                statistics["failed"] += 1
                continue

            landmarks.append(label)

            dataset.append(landmarks)

            statistics["successful"] += 1

    return dataset, statistics


# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":

    # Path relative to:
    # backend/app/ai/extract_landmarks.py
    dataset_path = "../../../datasets/asl_alphabet/asl_alphabet_train"

    dataset, statistics = process_dataset(dataset_path)

    print("\n========== DATASET SUMMARY ==========")
    print(f"Total Images      : {statistics['total_images']}")
    print(f"Successful        : {statistics['successful']}")
    print(f"Failed Detection  : {statistics['failed']}")
    print(f"Corrupted Images  : {statistics['corrupted']}")
    print("====================================")

    print(f"\nTotal Samples Extracted: {len(dataset)}")

    if dataset:

        print("\nFirst Sample:")
        print(dataset[0])

        print(f"\nNumber of Values: {len(dataset[0])}")

        if len(dataset[0]) == 64:
            print("\n✅ Correct! (63 landmarks + 1 label)")
        else:
            print("\n❌ Incorrect number of values.")