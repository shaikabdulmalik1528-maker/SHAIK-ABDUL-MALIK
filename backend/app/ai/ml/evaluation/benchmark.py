import os
import time
import joblib
import psutil
import pandas as pd

# -------------------------
# Load Model
# -------------------------

model = joblib.load("models/random_forest_model.pkl")

# -------------------------
# Load Test Data
# -------------------------

test_df = pd.read_csv("datasets/test.csv")

X_test = test_df.drop("label", axis=1)

# Use one sample for benchmarking
sample = X_test.iloc[[0]]

# -------------------------
# Average Inference Time
# -------------------------

runs = 1000

start = time.perf_counter()

for _ in range(runs):
    model.predict(sample)

end = time.perf_counter()

avg_inference_ms = ((end - start) / runs) * 1000

# -------------------------
# Memory Usage
# -------------------------

process = psutil.Process(os.getpid())

memory_mb = process.memory_info().rss / (1024 * 1024)

# -------------------------
# Model File Size
# -------------------------

model_size_mb = os.path.getsize(
    "models/random_forest_model.pkl"
) / (1024 * 1024)

# -------------------------
# Throughput
# -------------------------

throughput = 1000 / avg_inference_ms

# -------------------------
# CPU Utilization
# -------------------------

cpu_usage = psutil.cpu_percent(interval=1)

# -------------------------
# Print Results
# -------------------------

print("\n========== Benchmark Results ==========\n")

print(f"Average Inference Time : {avg_inference_ms:.4f} ms")
print(f"Memory Usage           : {memory_mb:.2f} MB")
print(f"Model Size             : {model_size_mb:.2f} MB")
print(f"Throughput             : {throughput:.2f} predictions/sec")
print(f"CPU Utilization        : {cpu_usage:.2f}%")

# -------------------------
# Save Benchmark Report
# -------------------------

os.makedirs("reports", exist_ok=True)

with open("reports/benchmark_report.md", "w") as f:

    f.write("# Benchmark Report\n\n")

    f.write(f"**Average Inference Time:** {avg_inference_ms:.4f} ms\n\n")

    f.write(f"**Memory Usage:** {memory_mb:.2f} MB\n\n")

    f.write(f"**Model Size:** {model_size_mb:.2f} MB\n\n")

    f.write(f"**Throughput:** {throughput:.2f} predictions/sec\n\n")

    f.write(f"**CPU Utilization:** {cpu_usage:.2f}%\n\n")

    f.write("## Conclusion\n\n")

    if avg_inference_ms < 10:
        f.write(
            "The Random Forest model is suitable for real-time webcam-based "
            "sign language recognition. The average inference time is well "
            "below 10 ms, enabling fast predictions suitable for live webcam "
            "applications. The model size is compact, memory usage is "
            "acceptable, and the throughput is high enough for real-time deployment."
        )
    else:
        f.write(
            "The model may not be suitable for real-time webcam-based sign "
            "language recognition because the inference time exceeds the "
            "desired real-time threshold."
        )

print("\n✅ benchmark_report.md created successfully!")
