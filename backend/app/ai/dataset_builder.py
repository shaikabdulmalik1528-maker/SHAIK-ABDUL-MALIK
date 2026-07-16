import os
import csv

from app.ai.extract_landmarks import process_dataset


# -----------------------------------
# Create CSV column names
# -----------------------------------
def create_columns():

    columns = []

    for i in range(21):
        columns.extend([
            f"x{i}",
            f"y{i}",
            f"z{i}"
        ])

    columns.append("label")

    return columns


# -----------------------------------
# Build Dataset CSV
# -----------------------------------
def build_dataset(
        dataset_path,
        output_file
):

    print("Starting dataset extraction...")

    dataset, statistics = process_dataset(
        dataset_path
    )


    columns = create_columns()


    print("Creating CSV...")


    with open(
        output_file,
        mode="w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        # Header
        writer.writerow(columns)


        # Data rows
        writer.writerows(dataset)


    print("\n========== DATASET BUILD SUMMARY ==========")

    print(
        f"Images Processed : {statistics['total_images']}"
    )

    print(
        f"Successful       : {statistics['successful']}"
    )

    print(
        f"Failed           : {statistics['failed']}"
    )

    print(
        f"Corrupted        : {statistics['corrupted']}"
    )

    print(
        f"CSV Location     : {output_file}"
    )

    print("==========================================")



# -----------------------------------
# Run Builder
# -----------------------------------
if __name__ == "__main__":


    dataset_path = "../../../datasets/asl_alphabet/asl_alphabet_train"


    output_file = "../../../datasets/landmarks.csv"


    build_dataset(
        dataset_path,
        output_file
    )