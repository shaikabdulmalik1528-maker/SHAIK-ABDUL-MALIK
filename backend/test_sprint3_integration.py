import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"
USER_ID = "test_malik"
SESSION_ID = "session_demo_101"

def run_sprint_integration_test():
    print("=== STARTING SPRINT 3 INTEGRATION TEST ===\n")

    # 1. First Attempt: Target 'A', predicted 'B' (Misclassification)
    print("1. Submitting incorrect attempt (Target: 'A', Predicted: 'B')...")
    payload_1 = {
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "target_alphabet": "A",
        "predicted_alphabet": "B",
        "confidence_score": 0.60
    }
    res_1 = requests.post(f"{BASE_URL}/assess", json=payload_1).json()
    print("   [Feedback]:", res_1["feedback"]["message"])
    print("   [Mastery Score]:", res_1["updated_learning_state"]["mastery_score"])
    print("   [Top Recommendation]:", res_1["next_recommendations"][0])
    print("-" * 60)

    # 2. Second Attempt: Same mistake to trigger Frequent Confusion
    print("\n2. Submitting second mistake to trigger confusion tracking...")
    res_2 = requests.post(f"{BASE_URL}/assess", json=payload_1).json()
    print("   [Feedback Type]:", res_2["feedback"]["type"])
    print("   [Top Recommendation Rationale]:", res_2["next_recommendations"][0]["rationale"])
    print("-" * 60)

    # 3. Third Attempt: Correct attempt for 'A' (Breakthrough)
    print("\n3. Submitting correct attempt for 'A' (Target: 'A', Predicted: 'A')...")
    payload_2 = {
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "target_alphabet": "A",
        "predicted_alphabet": "A",
        "confidence_score": 0.95
    }
    res_3 = requests.post(f"{BASE_URL}/assess", json=payload_2).json()
    print("   [Feedback Title]:", res_3["feedback"]["title"])
    print("   [Updated Mastery Score]:", res_3["updated_learning_state"]["mastery_score"])
    print("-" * 60)

    # 4. Dashboard Refresh Check
    print("\n4. Fetching Analytics Dashboard...")
    dash = requests.get(f"{BASE_URL}/dashboard/{USER_ID}").json()
    print(f"   [Total Sessions]: {dash['total_sessions']}")
    print(f"   [Total Attempts]: {dash['total_attempts']}")
    print(f"   [Overall Mastery]: {dash['overall_mastery']}")

    print("\n=== INTEGRATION TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_sprint_integration_test()
    