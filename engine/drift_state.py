class DriftState:
    def __init__(self, alpha=0.3):
        # alpha = smoothing factor (0–1)
        self.alpha = alpha
        self.current = 0.0
        self.history = []

    def update(self, drift_score):
        """
        Exponential smoothing:
        new_state = alpha * drift_score + (1 - alpha) * old_state
        """
        self.current = self.alpha * drift_score + (1 - self.alpha) * self.current
        self.history.append(self.current)
        return self.current

    def get_state(self):
        return self.current
