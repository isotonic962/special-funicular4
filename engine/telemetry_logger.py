import sqlite3
import datetime

class TelemetryLogger:
    def __init__(self, db_path="moberg_telemetry.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates the telemetry table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS engine_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_prompt TEXT,
                final_output TEXT,
                sentiment_raw REAL,
                volatility_raw REAL,
                entropy_raw REAL,
                drift_score REAL,
                engine_state TEXT,
                mode TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def log_event(self, prompt, output, analysis, drift_score, state, mode):
        """Call this at the very end of your engine.process() loop."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        timestamp = datetime.datetime.now().isoformat()
        
        c.execute('''
            INSERT INTO engine_logs (
                timestamp, user_prompt, final_output, 
                sentiment_raw, volatility_raw, entropy_raw, 
                drift_score, engine_state, mode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, prompt, output, 
            analysis["sentiment"], analysis["volatility"], analysis["entropy"],
            drift_score, state, mode
        ))
        
        conn.commit()
        conn.close()