import sqlite3
from error_analysis import ErrorAnalysisModule

# 1. Populate temporary dummy attempts into the database
conn = sqlite3.connect("app_data.db")
cursor = conn.cursor()

sample_attempts = [
    # User tries 'M', fails with 'N' across 2 sessions
    ("a1", "user_1", "sess_1", "M", "N", 0.52, 0),
    ("a2", "user_1", "sess_1", "M", "N", 0.58, 0),
    ("a3", "user_1", "sess_2", "M", "N", 0.60, 0),
    # User gets 'A' correct reliably
    ("a4", "user_1", "sess_1", "A", "A", 0.95, 1),
    ("a5", "user_1", "sess_2", "A", "A", 0.92, 1),
]

cursor.executemany(
    """
    INSERT OR REPLACE INTO prediction_attempts 
    (id, user_id, session_id, target_alphabet, predicted_alphabet, confidence_score, is_correct)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, 
    sample_attempts
)
conn.commit()
conn.close()

# 2. Run the Error Analysis Module
analyzer = ErrorAnalysisModule(db_path="app_data.db")
report = analyzer.analyze_user_performance(user_id="user_1")

# 3. Print the structured JSON result
import json
print(json.dumps(report, indent=2))