class DriftModeClassifier:
    def __init__(self, stable_threshold=12, critical_threshold=20):
        self.stable_threshold = stable_threshold
        self.critical_threshold = critical_threshold

    def classify(self, drift_state):
        if drift_state < self.stable_threshold:
            return "stable"
        elif drift_state < self.critical_threshold:
            return "unstable"
        else:
            return "critical"
