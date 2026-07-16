import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

# Load datasets
train_df = pd.read_csv("datasets/train.csv")

X_train = train_df.drop("label", axis=1)
y_train = train_df["label"]

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Create models directory if needed
os.makedirs("models", exist_ok=True)

# Save model
joblib.dump(model, "models/random_forest_model.pkl")

print("✅ Model saved to models/random_forest_model.pkl")
