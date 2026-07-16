from backend.app.ai.utils.experiment_tracker import create_experiment


create_experiment(
    experiment_id="experiment_001",
    dataset_version="normalized_landmarks_v1",
    feature_version="mediapipe_normalized_v1",
    model_name="RandomForestClassifier",
    parameters={
        "n_estimators": 100,
        "max_depth": None,
        "min_samples_leaf": 1,
        "random_state": 42
    },
    engineer_name="Abdul Malik"
)
