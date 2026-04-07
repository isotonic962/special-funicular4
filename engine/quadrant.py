class QuadrantClassifier:
    def __init__(
        self,
        vol_spike=5.0,
        vol_floor=1.0,
        ent_spike=6.7,
        ent_collapse=5.9
    ):
        self.vol_spike = vol_spike
        self.vol_floor = vol_floor
        self.ent_spike = ent_spike
        self.ent_collapse = ent_collapse

    def classify(self, volatility, entropy):
        """
        Returns a quadrant label and a recommended controller action.

        Quadrants:
        Q1 — High vol + High ent   → EXPRESSIVE FLAIL
        Q2 — High vol + Low ent    → EXPRESSIVE COLLAPSE
        Q3 — Low vol  + Any ent    → FLAT / ALLOW TEXTURE
        Q4 — Stable vol + Stable ent → NOMINAL
        """
        high_vol = volatility > self.vol_spike
        low_vol = volatility < self.vol_floor
        high_ent = entropy > self.ent_spike
        low_ent = entropy < self.ent_collapse

        if high_vol and high_ent:
            return {
                "quadrant": "Q1",
                "label": "expressive_flail",
                "action": "downweight_expressive",
                "description": "High volatility + high entropy. Model is flailing. Prefer procedural continuation."
            }
        elif high_vol and low_ent:
            return {
                "quadrant": "Q2",
                "label": "expressive_collapse",
                "action": "prevent_truncation",
                "description": "High volatility + low entropy. Model collapsing to minimal utterance. Force continuation."
            }
        elif low_vol:
            return {
                "quadrant": "Q3",
                "label": "flat",
                "action": "allow_texture",
                "description": "Low volatility. Output is flat. Allow minimal expressive texture."
            }
        else:
            return {
                "quadrant": "Q4",
                "label": "nominal",
                "action": "default",
                "description": "Stable volatility and entropy. Default constrained generation."
            }
