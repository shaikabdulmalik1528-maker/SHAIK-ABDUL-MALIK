import os
import csv


class DatasetExplorer:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path

    def analyze(self):
        class_counts = {}
        total_images = 0

        for class_name in sorted(os.listdir(self.dataset_path)):
            class_path = os.path.join(self.dataset_path, class_name)

            if not os.path.isdir(class_path):
                continue

            images = [
                image
                for image in os.listdir(class_path)
                if image.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                )
            ]

            count = len(images)

            class_counts[class_name] = count
            total_images += count

        return class_counts, total_images

    def export_csv(self, class_counts, total_images, output_file):
        largest = max(class_counts, key=class_counts.get)
        smallest = min(class_counts, key=class_counts.get)

        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(["Gesture Class", "Images"])

            for cls, count in class_counts.items():
                writer.writerow([cls, count])

            writer.writerow([])
            writer.writerow(["Total Classes", len(class_counts)])
            writer.writerow(["Total Images", total_images])
            writer.writerow(["Largest Class", largest])
            writer.writerow(["Smallest Class", smallest])

        print("\nDataset Analysis Complete\n")

        print("Total Classes :", len(class_counts))
        print("Total Images  :", total_images)
        print("Largest Class :", largest)
        print("Smallest Class:", smallest)

        print(f"\nCSV saved as: {output_file}")