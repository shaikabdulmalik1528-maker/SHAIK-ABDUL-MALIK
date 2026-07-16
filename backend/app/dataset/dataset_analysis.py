import os

from ai.utils.dataset_explorer import DatasetExplorer


dataset_path = os.path.join(
    "..",
    "..",
    "datasets",
    "asl_alphabet"
    "asl_alphabet_train",
)

explorer = DatasetExplorer(dataset_path)

class_counts, total_images = explorer.analyze()

explorer.export_csv(
    class_counts,
    total_images,
    "dataset_report.csv",
)