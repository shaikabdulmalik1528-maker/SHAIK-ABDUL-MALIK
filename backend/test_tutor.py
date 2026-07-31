import json
from tutor_service import IntelligentTutorService

tutor = IntelligentTutorService(db_path="app_data.db")

# Simulate a new prediction event where user fails 'M' again
result = tutor.process_prediction_event(
    user_id="user_1",
    session_id="sess_3",
    target="M",
    predicted="N",
    confidence=0.74
)

print("--- INTELLIGENT TUTOR OUTPUT ---")
print(json.dumps(result, indent=2))
