import os
import json

from app.ai.extract_landmarks import process_dataset


def validate_dataset(dataset_path, output_file):
    """
    Validate the dataset and generate a JSON report.
    """

    print("Starting dataset validation...")

    _, statistics = process_dataset(dataset_path)

    success_percentage = 0.0

    if statistics["total_images"] > 0:
        success_percentage = round(
            (statistics["successful"] / statistics["total_images"]) * 100,
            2
        )

    report = {
        "total_images": statistics["total_images"],
        "successful_detections": statistics["successful"],
        "failed_detections": statistics["failed"],
        "corrupted_images": statistics["corrupted"],
        "success_percentage": success_percentage
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as file:
        json.dump(report, file, indent=4)

    print("\n========== VALIDATION REPORT ==========")

    for key, value in report.items():
        print(f"{key}: {value}")

    print("=======================================")
    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":

    dataset_path = "../../../datasets/asl_alphabet/asl_alphabet_train"

    output_file = "../../../datasets/dataset_report.json"

    validate_dataset(dataset_path, output_file)