import os

from app.ai.dataset_builder import build_dataset
from app.ai.validator import validate_dataset


class PreprocessingService:
    """
    Service responsible for running the
    complete preprocessing pipeline.
    """

    def run(self):
        base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                ".."
            )
        )

        dataset_path = os.path.join(
            base_dir,
            "datasets",
            "asl_alphabet",
            "asl_alphabet_train"
        )

        csv_output = os.path.join(
            base_dir,
            "datasets",
            "landmarks.csv"
        )

        report_output = os.path.join(
            base_dir,
            "datasets",
            "dataset_report.json"
        )

        print("\nStarting preprocessing pipeline...\n")

        build_dataset(
            dataset_path=dataset_path,
            output_file=csv_output
        )

        validate_dataset(
            dataset_path=dataset_path,
            output_file=report_output
        )

        return {
            "success": True,
            "message": "Dataset preprocessing completed.",
            "data": {
                "csv_file": csv_output,
                "report_file": report_output
            }
        }