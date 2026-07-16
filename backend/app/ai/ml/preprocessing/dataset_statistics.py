import json
import pandas as pd

# ==============================
# File Paths
# ==============================
NORMALIZED_FILE = "datasets/normalized_landmarks.csv"
TRAIN_FILE = "datasets/train.csv"
VALIDATION_FILE = "datasets/validation.csv"
TEST_FILE = "datasets/test.csv"
OUTPUT_FILE = "datasets/training_report.json"

# If you know how many images failed during landmark extraction,
# update this value accordingly.
FAILED_LANDMARK_EXTRACTIONS = 0


def main():
    # Read datasets
    normalized_df = pd.read_csv(NORMALIZED_FILE)
    train_df = pd.read_csv(TRAIN_FILE)
    validation_df = pd.read_csv(VALIDATION_FILE)
    test_df = pd.read_csv(TEST_FILE)

    # Dataset statistics
    total_samples = len(normalized_df)
    gesture_classes = normalized_df["label"].nunique()
    samples_per_class = (
        normalized_df["label"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    number_of_features = len(normalized_df.columns) - 1

    training_set_size = len(train_df)
    validation_set_size = len(validation_df)
    test_set_size = len(test_df)

    # Report dictionary
    report = {
        "total_samples": total_samples,
        "number_of_gesture_classes": gesture_classes,
        "samples_per_class": samples_per_class,
        "number_of_features": number_of_features,
        "training_set_size": training_set_size,
        "validation_set_size": validation_set_size,
        "test_set_size": test_set_size,
        "failed_landmark_extraction_count": FAILED_LANDMARK_EXTRACTIONS
    }

    # Save JSON
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=4)

    # Print summary
    print("=" * 50)
    print("Training Report Generated Successfully")
    print("=" * 50)

    print(f"Total Samples              : {total_samples}")
    print(f"Gesture Classes            : {gesture_classes}")
    print(f"Number of Features         : {number_of_features}")
    print(f"Training Samples           : {training_set_size}")
    print(f"Validation Samples         : {validation_set_size}")
    print(f"Test Samples               : {test_set_size}")
    print(f"Failed Landmark Extractions: {FAILED_LANDMARK_EXTRACTIONS}")

    print("\nSamples Per Class")
    print("-" * 50)

    for label, count in samples_per_class.items():
        print(f"{label:<10} : {count}")

    print("\nTraining report saved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()