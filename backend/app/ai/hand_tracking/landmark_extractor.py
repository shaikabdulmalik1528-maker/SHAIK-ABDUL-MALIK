class LandmarkExtractor:
    def extract(self, results):
        """
        Extract all landmarks from MediaPipe results.

        Returns:
            List of hands.
            Each hand contains 21 landmarks.
        """

        hands_data = []

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                current_hand = []

                for landmark in hand_landmarks.landmark:

                    current_hand.append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z
                    })

                hands_data.append(current_hand)

        return hands_data