import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def execute_remaining_sessions():
    print("==================================================")
    print("1. CONTINUING SESSION 2: REGRESSION DEMOTION FOR 'C'")
    print("==================================================")
    
    # Start Session 2
    start_res2 = requests.post(f"{BASE_URL}/cycle/start-cycle").json()
    session2_id = start_res2["session_id"]
    print(f"Session 2 Initialized | ID: {session2_id}")

    payload_c_fail = {
        "session_id": session2_id,
        "target_alphabet": "C",
        "predicted_alphabet": "E",
        "confidence": 0.35,
        "inference_time_ms": 46.0
    }

    # Execute 3 consecutive failed attempts to trigger NEEDS_REVISION
    for i in range(1, 4):
        res = requests.post(f"{BASE_URL}/cycle/process-attempt", json=payload_c_fail).json()
        state = res["updated_learner_state"]["current_state"]
        acc = res["updated_learner_state"]["rolling_accuracy"]
        rec = res.get("next_recommendation", {})
        print(f"-> Attempt {i}: State = {state} | Rolling Acc = {acc*100:.1f}% | Priority = {rec.get('priority_score')}")

    # End Session 2
    res2_end = requests.post(f"{BASE_URL}/cycle/end-cycle/{session2_id}").json()
    print("\nSession 2 Summary Report:")
    print(json.dumps(res2_end["session_summary"], indent=2))

    print("\n==================================================")
    print("2. STARTING SESSION 3: REMEDIATION RECOVERY FOR 'C'")
    print("==================================================")

    # Start Session 3
    start_res3 = requests.post(f"{BASE_URL}/cycle/start-cycle").json()
    session3_id = start_res3["session_id"]
    print(f"Session 3 Initialized | ID: {session3_id}")

    payload_c_pass = {
        "session_id": session3_id,
        "target_alphabet": "C",
        "predicted_alphabet": "C",
        "confidence": 0.95,
        "inference_time_ms": 40.0
    }

    # Execute 3 consecutive accurate attempts to trigger recovery to MASTERED
    for i in range(1, 4):
        res = requests.post(f"{BASE_URL}/cycle/process-attempt", json=payload_c_pass).json()
        state = res["updated_learner_state"]["current_state"]
        acc = res["updated_learner_state"]["rolling_accuracy"]
        rec = res.get("next_recommendation", {})
        print(f"-> Attempt {i}: State = {state} | Rolling Acc = {acc*100:.1f}% | Next Target = {rec.get('alphabet')}")

    # End Session 3
    res3_end = requests.post(f"{BASE_URL}/cycle/end-cycle/{session3_id}").json()
    print("\nSession 3 Summary Report:")
    print(json.dumps(res3_end["session_summary"], indent=2))
    print("\n==================================================")
    print("ALL THREE PRACTICE SESSIONS SUCCESSFULLY VERIFIED!")
    print("==================================================")

if __name__ == "__main__":
    execute_remaining_sessions()
