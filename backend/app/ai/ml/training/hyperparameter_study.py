import time
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

# -------------------------
# Load datasets
# -------------------------

train_df = pd.read_csv("datasets/train.csv")
test_df = pd.read_csv("datasets/test.csv")

X_train = train_df.drop("label", axis=1)
y_train = train_df["label"]

X_test = test_df.drop("label", axis=1)
y_test = test_df["label"]

# -------------------------
# Hyperparameter values
# -------------------------

tree_values = [50, 100, 200]

results = []

# -------------------------
# Train and Evaluate
# -------------------------

for trees in tree_values:

    print(f"\nTraining Random Forest with {trees} trees...")

    model = RandomForestClassifier(
        n_estimators=trees,
        random_state=42
    )

    start = time.time()

    model.fit(X_train, y_train)

    training_time = time.time() - start

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    f1 = f1_score(
        y_test,
        predictions,
        average="weighted"
    )

    results.append({
        "n_estimators": trees,
        "Training Time (seconds)": round(training_time, 4),
        "Accuracy": round(accuracy, 4),
        "F1 Score": round(f1, 4)
    })

# -------------------------
# Save Results
# -------------------------

report = pd.DataFrame(results)

report.to_csv("hyperparameter_study.csv", index=False)

print("\nHyperparameter Study Report:")
print(report.to_string(index=False))

print("\n✅ hyperparameter_study.csv created successfully!")
