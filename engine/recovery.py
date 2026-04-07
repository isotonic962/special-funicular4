class DriftRecovery:
    def __init__(self, anchor=0.0, decay=0.05):
        """
        anchor: the baseline drift value the system returns to
        decay: how fast the system recovers per message (0–1)
        """
        self.anchor = anchor
        self.decay = decay

    def apply(self, state_value):
        """
        Pull the state slightly toward the anchor.
        new_state = state - decay * (state - anchor)
        """
        return state_value - self.decay * (state_value - self.anchor)
