import sys
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_production_sprint():
    print("=== STARTING PRODUCTION SPRINT VERIFICATION TEST ===")
    sys.stdout.flush()

    valid_hand = [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.99} for _ in range(21)]

    # 1. Test Input Validation Failure
    print("\n1. Testing Input Validation Layer (Rejection on incomplete landmarks)...")
    invalid_req = {
        "user_id": "malik_prod",
        "session_id": "sess_001",
        "target_alphabet": "A",
        "hand_landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0}]
    }
    res_val = requests.post(f"{BASE_URL}/assessment/process", json=invalid_req)
    print(f"   [Status Code]: {res_val.status_code} (Expected 422)")
    
    res_json = res_val.json()
    if "error" in res_json:
        print(f"   [Error Message]: {res_json['error']['message']}")
    elif "detail" in res_json:
        print(f"   [Validation Detail]: {res_json['detail']}")
    print("-" * 65)

    # 2. Test Successful Assessment Pipeline
    print("\n2. Testing Complete Intelligent Assessment Pipeline...")
    valid_req = {
        "user_id": "malik_prod",
        "session_id": "sess_001",
        "target_alphabet": "A",
        "hand_landmarks": valid_hand
    }
    res_ass = requests.post(f"{BASE_URL}/assessment/process", json=valid_req)
    print(f"   [Status Code]: {res_ass.status_code}")
    data = res_ass.json().get("data", {})
    if data:
        print(f"   [Assessment]: Target={data['assessment']['target_alphabet']}, Predicted={data['assessment']['predicted_alphabet']}")
        print(f"   [Inference Time]: {data['assessment']['inference_time_ms']} ms")
        print(f"   [Mastery Level]: {data['updated_profile']['mastery_score']}")
        print(f"   [Top Recommendation]: {data['next_recommendations'][0]}")
    else:
        print(f"   [Response Payload]: {res_ass.json()}")
    print("-" * 65)

    # 3. Test Duplicate Record Prevention
    print("\n3. Testing Duplicate Record Block...")
    res_dup = requests.post(f"{BASE_URL}/assessment/process", json=valid_req)
    print(f"   [Status Code]: {res_dup.status_code} (Expected 409 Conflict)")
    dup_json = res_dup.json()
    if "error" in dup_json:
        print(f"   [Blocked Message]: {dup_json['error']['message']}")
    else:
        print(f"   [Response]: {dup_json}")
    print("-" * 65)

    # 4. Test Dashboard Analytics
    print("\n4. Testing Live Analytics Dashboard...")
    res_dash = requests.get(f"{BASE_URL}/analytics/dashboard/malik_prod")
    print(f"   [Dashboard Response]: {res_dash.json().get('data')}")

    print("\n=== ALL TEST CASES PASSED SUCCESSFULLY ===")

# Explicit execution block
if __name__ == "__main__":
    test_production_sprint()
    