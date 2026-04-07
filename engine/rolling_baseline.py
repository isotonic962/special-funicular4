import sqlite3
import statistics

class RollingBaseline:
    def __init__(self, db_path="moberg_telemetry.db", window=3):
        self.db_path = db_path
        self.window = window

        # Thresholds derived from telemetry data
        self.vol_spike = 4.0
        self.vol_floor = 1.0
        self.ent_spike = 6.7
        self.ent_collapse = 5.9

        # Generation parameter sets per quadrant action
        self.params = {
            "downweight_expressive": {
                "temperature": 0.5,
                "repeat_penalty": 1.3
            },
            "prevent_truncation": {
                "temperature": 0.6,
                "repeat_penalty": 1.05
            },
            "allow_texture": {
                "temperature": 0.8,
                "repeat_penalty": 1.1
            },
            "default": {
                "temperature": 0.7,
                "repeat_penalty": 1.1
            },
            "suppress_labeling": {
                "temperature": 0.55,
                "repeat_penalty": 1.2
            },
            "constrain_options": {
                "temperature": 0.5,
                "repeat_penalty": 1.15
            }
        }

    def get_window(self):
        """Fetch last N volatility and entropy readings from db."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT volatility_raw, entropy_raw, sentiment_raw
                FROM engine_logs
                ORDER BY id DESC
                LIMIT ?
            """, (self.window,))
            rows = c.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def get_rolling_averages(self):
        """Calculate recency-weighted averages from window.
        Most recent entry has highest weight, oldest has lowest."""
        rows = self.get_window()
        if not rows:
            return None, None, None
        # rows are ordered DESC so index 0 is most recent
        weights = [3, 2, 1][:len(rows)]
        total_weight = sum(weights)
        avg_vol = sum(r[0] * w for r, w in zip(rows, weights)) / total_weight
        avg_ent = sum(r[1] * w for r, w in zip(rows, weights)) / total_weight
        avg_sent = sum(r[2] * w for r, w in zip(rows, weights)) / total_weight
        return avg_vol, avg_ent, avg_sent

    def recommend(self, avg_sentiment=None):
        """
        Returns recommended generation parameters based on
        rolling volatility and entropy averages.
        """
        avg_vol, avg_ent, avg_sent = self.get_rolling_averages()

        # No history yet — use defaults
        if avg_vol is None:
            return self.params["default"], "default", None, None

        high_vol = avg_vol > self.vol_spike
        low_vol = avg_vol < self.vol_floor
        high_ent = avg_ent > self.ent_spike
        low_ent = avg_ent < self.ent_collapse

        high_sent = avg_sent is not None and avg_sent > 2.0

        if high_vol and high_ent:
            action = "downweight_expressive"
        elif high_vol and low_ent:
            action = "prevent_truncation"
        elif low_vol:
            action = "allow_texture"
        elif high_sent and not high_vol:
            action = "suppress_labeling"
        elif high_ent and not high_vol:
            action = "constrain_options"
        else:
            action = "default"

        return self.params[action], action, round(avg_vol, 2), round(avg_ent, 2)
