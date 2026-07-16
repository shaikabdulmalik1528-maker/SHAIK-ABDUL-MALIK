import os
import pandas as pd

# File paths
INPUT_FILE = "datasets/landmarks.csv"
OUTPUT_FILE = "datasets/normalized_landmarks.csv"


def normalize_row(row):
    """
    Normalize landmarks using wrist-relative coordinates.
    Wrist (landmark 0) becomes the origin (0, 0, 0).
    """

    wrist_x = row["x0"]
    wrist_y = row["y0"]
    wrist_z = row["z0"]

    normalized = row.copy()

    for i in range(21):
        normalized[f"x{i}"] = row[f"x{i}"] - wrist_x
        normalized[f"y{i}"] = row[f"y{i}"] - wrist_y
        normalized[f"z{i}"] = row[f"z{i}"] - wrist_z

    return normalized


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Read dataset
    df = pd.read_csv(INPUT_FILE)

    # Separate features and label
    labels = df["label"]
    features = df.drop(columns=["label"])

    # Normalize each sample
    normalized_features = features.apply(normalize_row, axis=1)

    # Add labels back
    normalized_features["label"] = labels

    # Save normalized dataset
    normalized_features.to_csv(OUTPUT_FILE, index=False)

    print("========================================")
    print("Normalization Completed Successfully")
    print("========================================")
    print(f"Input File : {INPUT_FILE}")
    print(f"Output File: {OUTPUT_FILE}")
    print(f"Total Samples: {len(normalized_features)}")


if __name__ == "__main__":
    main()
    