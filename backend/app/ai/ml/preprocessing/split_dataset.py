import pandas as pd
from sklearn.model_selection import train_test_split

# File paths
INPUT_FILE = "datasets/normalized_landmarks.csv"
TRAIN_FILE = "datasets/train.csv"
VALIDATION_FILE = "datasets/validation.csv"
TEST_FILE = "datasets/test.csv"


def main():
    # Read normalized dataset
    df = pd.read_csv(INPUT_FILE)

    # -----------------------------------------
    # Remove rare classes before stratified split
    # -----------------------------------------
    class_counts = df["label"].value_counts()
    rare_classes = class_counts[class_counts < 4].index.tolist()

    if rare_classes:
        print("=" * 50)
        print(f"Removing rare classes: {rare_classes}")
        print("Reason: Not enough samples for stratified train/validation/test split.")
        print("=" * 50)

        df = df[~df["label"].isin(rare_classes)]

    # Features and Labels
    X = df.drop(columns=["label"])
    y = df["label"]

    # -------------------------
    # First Split
    # 70% Train
    # 30% Temp
    # -------------------------
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        stratify=y,
        random_state=42,
    )

    # -------------------------
    # Second Split
    # 15% Validation
    # 15% Test
    # -------------------------
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=42,
    )

    # Create DataFrames
    train_df = X_train.copy()
    train_df["label"] = y_train.values

    val_df = X_val.copy()
    val_df["label"] = y_val.values

    test_df = X_test.copy()
    test_df["label"] = y_test.values

    # Save CSV files
    train_df.to_csv(TRAIN_FILE, index=False)
    val_df.to_csv(VALIDATION_FILE, index=False)
    test_df.to_csv(TEST_FILE, index=False)

    # -------------------------
    # Print Summary
    # -------------------------
    print("\n" + "=" * 50)
    print("Dataset Split Completed Successfully")
    print("=" * 50)

    print(f"Training Samples   : {len(train_df)}")
    print(f"Validation Samples : {len(val_df)}")
    print(f"Test Samples       : {len(test_df)}")
    print(f"Total Samples      : {len(df)}")

    print("\nClass Distribution")
    print("-" * 50)

    distribution = pd.DataFrame({
        "Train": y_train.value_counts().sort_index(),
        "Validation": y_val.value_counts().sort_index(),
        "Test": y_test.value_counts().sort_index()
    }).fillna(0).astype(int)

    print(distribution)

    print("\nSplit files generated successfully:")
    print(f"✔ {TRAIN_FILE}")
    print(f"✔ {VALIDATION_FILE}")
    print(f"✔ {TEST_FILE}")


if __name__ == "__main__":
    main()