import sqlite3

# 1. This creates a local database file named 'app_data.db' automatically
connection = sqlite3.connect("app_data.db")
cursor = connection.cursor()

# 2. This is the blueprint for your 3 tables
tables_schema = """
CREATE TABLE IF NOT EXISTS prediction_attempts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    target_alphabet TEXT NOT NULL,
    predicted_alphabet TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    is_correct INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_alphabet_mastery (
    user_id TEXT NOT NULL,
    alphabet TEXT NOT NULL,
    mastery_level TEXT DEFAULT 'NOT_STARTED',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, alphabet)
);

CREATE TABLE IF NOT EXISTS assessment_feedback_history (
    id TEXT PRIMARY KEY,
    attempt_id TEXT,
    feedback_type TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    action_item TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 3. Run the blueprint to build the tables inside the file
cursor.executescript(tables_schema)
connection.commit()
connection.close()

print("Success! Your database file 'app_data.db' has been created with all 3 tables.")
