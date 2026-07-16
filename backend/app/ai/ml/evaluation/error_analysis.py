import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

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
# Train Random Forest
# -------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

# -------------------------
# Confusion Matrix
# -------------------------

labels = sorted(y_test.unique())

cm = confusion_matrix(y_test, predictions, labels=labels)

# Save image
os.makedirs("reports", exist_ok=True)

plt.figure(figsize=(12, 12))

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=labels
)

disp.plot(
    cmap="Blues",
    xticks_rotation=90
)

plt.title("Confusion Matrix")

plt.savefig("reports/confusion_matrix.png", dpi=300)

plt.close()

print("✅ Confusion matrix saved.")

# -------------------------
# Top 5 Most Confused Gestures
# -------------------------

cm_copy = cm.copy()

np.fill_diagonal(cm_copy, 0)

confused_pairs = []

for i in range(len(labels)):
    for j in range(len(labels)):
        if cm_copy[i][j] > 0:
            confused_pairs.append(
                (
                    labels[i],
                    labels[j],
                    cm_copy[i][j]
                )
            )

confused_pairs.sort(
    key=lambda x: x[2],
    reverse=True
)

top5 = confused_pairs[:5]

print("\nTop 5 Most Confused Gestures\n")

for actual, predicted, count in top5:
    print(
        f"Actual: {actual} -> Predicted: {predicted} ({count} times)"
    )
    