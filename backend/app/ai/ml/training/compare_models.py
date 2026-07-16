import time
import pandas as pd

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

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
# Models
# -------------------------

models = {
    "Decision Tree": DecisionTreeClassifier(random_state=42),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42
    ),

    "Support Vector Machine": SVC(
        kernel="rbf",
        random_state=42
    )
}

results = []

# -------------------------
# Train & Evaluate
# -------------------------

for name, model in models.items():

    start = time.time()

    model.fit(X_train, y_train)

    training_time = time.time() - start

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    precision = precision_score(
        y_test,
        predictions,
        average="weighted"
    )

    recall = recall_score(
        y_test,
        predictions,
        average="weighted"
    )

    f1 = f1_score(
        y_test,
        predictions,
        average="weighted"
    )

    results.append({
        "Algorithm": name,
        "Training Time (seconds)": round(training_time, 4),
        "Accuracy": round(accuracy, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1 Score": round(f1, 4)
    })

# -------------------------
# Save report
# -------------------------

report = pd.DataFrame(results)

report.to_csv("comparison_report.csv", index=False)

print("\nComparison Report:")
print(report.to_string(index=False))

print("\n✅ comparison_report.csv created successfully!")
