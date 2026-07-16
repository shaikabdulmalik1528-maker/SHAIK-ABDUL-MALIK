import json
import os
from datetime import datetime


class JSONSaver:

    def __init__(self):
        # backend/captures folder
        self.capture_folder = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "captures"
            )
        )

        os.makedirs(self.capture_folder, exist_ok=True)

    def save(self, hands_data):

        # Count existing JSON files
        existing = [
            file for file in os.listdir(self.capture_folder)
            if file.endswith(".json")
        ]

        filename = f"capture_{len(existing)+1:03d}.json"

        filepath = os.path.join(self.capture_folder, filename)

        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hands": []
        }

        for hand_index, hand in enumerate(hands_data):

            data["hands"].append({
                "hand_number": hand_index + 1,
                "landmarks": hand
            })

        with open(filepath, "w") as file:
            json.dump(data, file, indent=4)

        print(f"\n✅ Saved: {filename}")