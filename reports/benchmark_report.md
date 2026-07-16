# Benchmark Report

## Inference Benchmark Results

| Metric | Result |
|--------|--------|
| Average Inference Time | 7.7812 ms |
| Memory Usage | 244.82 MB |
| Model Size | 80.12 MB |
| Throughput | 128.51 predictions/second |
| CPU Utilization | 1.00% |

## Analysis

### Average Inference Time

The model requires approximately **7.78 milliseconds** to classify a single hand gesture. This is well below the commonly accepted real-time threshold of **10 milliseconds per prediction**, making it suitable for live webcam applications.

### Memory Usage

The benchmark recorded approximately **244.82 MB** of memory usage during inference. This memory requirement is acceptable for modern desktop and laptop systems.

### Model Size

The trained Random Forest model occupies **80.12 MB** of storage. While larger than some simpler models, this size is reasonable for deployment on desktop systems and does not significantly impact performance.

### Throughput

The model can process approximately **128.51 predictions per second**, which is significantly higher than the frame rate of a standard webcam (typically 30 FPS). This indicates that the model can comfortably perform real-time gesture recognition without becoming a bottleneck.

### CPU Utilization

CPU utilization during benchmarking was approximately **1.00%**, indicating that inference is computationally efficient and leaves sufficient processing resources for webcam capture and user interface tasks.

## Conclusion

Based on the benchmark results, the Random Forest model is **suitable for real-time webcam-based sign language recognition**.

The model achieves an average inference time of **7.78 ms**, which is below the 10 ms target for real-time systems. It also provides a throughput of over **128 predictions per second**, exceeding the requirements of standard webcam frame rates. Memory usage and CPU utilization remain within acceptable limits, making the model appropriate for deployment in a live sign language learning platform.
