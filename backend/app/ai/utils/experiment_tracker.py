import os
import json
from datetime import datetime


def create_experiment(
    experiment_id,
    dataset_version,
    feature_version,
    model_name,
    parameters,
    engineer_name,
):
    """
    Create an experiment folder and save configuration.
    """

    folder = os.path.join("experiments", experiment_id)
    os.makedirs(folder, exist_ok=True)

    config = {
        "experiment_id": experiment_id,
        "dataset_version": dataset_version,
        "feature_version": feature_version,
        "model": model_name,
        "parameters": parameters,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "engineer": engineer_name,
    }

    with open(os.path.join(folder, "experiment_config.json"), "w") as f:
        json.dump(config, f, indent=4)

    with open(os.path.join(folder, "results.json"), "w") as f:
        json.dump({}, f, indent=4)

    with open(os.path.join(folder, "notes.md"), "w") as f:
        f.write("# Experiment Notes\n\n")

    print(f"✅ Created {experiment_id}")


def save_results(experiment_id, metrics):
    """
    Save evaluation metrics to results.json.
    """

    folder = os.path.join("experiments", experiment_id)

    with open(os.path.join(folder, "results.json"), "w") as f:
        json.dump(metrics, f, indent=4)

    print("✅ Results saved")
    