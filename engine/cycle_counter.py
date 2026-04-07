class CycleCounter:
    """
    Tracks action cycles since last constraint and decides when to terminate.

    An action cycle = constraint → resistance → continuation.
    Termination fires when cycles_since_constraint >= N (modified by drift state).
    Secondary trigger: consecutive non-constraint sentences with rising sentiment.
    """

    def __init__(self, base_n=2, min_tokens=120):
        self.base_n = base_n
        self.min_tokens = min_tokens

        # Drift/volatility modifiers
        self.vol_high = 4.0
        self.drift_force_terminate = 15.0

        # Secondary trigger: consecutive non-constraints with rising sentiment
        self.reflection_streak_limit = 3

        # State
        self.cycles_since_constraint = 0
        self.total_constraints = 0
        self.sentence_count = 0
        self.token_count = 0
        self.consecutive_non_constraints = 0
        self.sentiment_window = []  # per-sentence sentiment scores
        self.last_constraint_index = -1
        self.terminated = False
        self.termination_reason = None

    def _effective_n(self, volatility=0.0, drift_score=0.0):
        """
        Adjust N based on current engine state.
        Higher volatility = lower N (cut sooner).
        """
        n = self.base_n

        if drift_score >= self.drift_force_terminate:
            return 0  # force immediate termination

        if volatility > self.vol_high:
            n = max(1, n - 1)

        return n

    def _estimate_tokens(self, sentence):
        # Rough estimate: 1 token ≈ 0.75 words
        return int(len(sentence.split()) / 0.75)

    def _rising_sentiment(self):
        """Check if per-sentence sentiment is trending upward."""
        if len(self.sentiment_window) < 2:
            return False
        recent = self.sentiment_window[-3:]
        if len(recent) < 2:
            return False
        # Rising if each score >= previous
        return all(recent[i] >= recent[i - 1] for i in range(1, len(recent))) and recent[-1] > 0

    def update(self, constraint_result, sentence, sentence_sentiment=0.0,
               current_volatility=0.0, current_drift=0.0):
        """
        Feed one sentence through the counter.

        Returns:
        {
            "sentence_index": int,
            "terminate": bool,
            "reason": str or None,
            "cycles_since_constraint": int,
            "effective_n": int
        }
        """
        if self.terminated:
            return {
                "sentence_index": self.sentence_count,
                "terminate": True,
                "reason": self.termination_reason,
                "cycles_since_constraint": self.cycles_since_constraint,
                "effective_n": 0,
            }

        self.sentence_count += 1
        self.token_count += self._estimate_tokens(sentence)
        self.sentiment_window.append(sentence_sentiment)

        is_constraint = constraint_result["is_constraint"]
        confidence = constraint_result["confidence"]

        # Only count high-confidence constraints
        if is_constraint and confidence >= 0.5:
            self.total_constraints += 1
            self.cycles_since_constraint = 0
            self.consecutive_non_constraints = 0
            self.last_constraint_index = self.sentence_count - 1
        else:
            self.cycles_since_constraint += 1
            self.consecutive_non_constraints += 1

        # Don't terminate before minimum length
        if self.token_count < self.min_tokens:
            return {
                "sentence_index": self.sentence_count - 1,
                "terminate": False,
                "reason": None,
                "cycles_since_constraint": self.cycles_since_constraint,
                "effective_n": self._effective_n(current_volatility, current_drift),
            }

        effective_n = self._effective_n(current_volatility, current_drift)

        # Primary trigger: cycles since constraint >= N
        if self.cycles_since_constraint >= effective_n and self.total_constraints > 0:
            self.terminated = True
            self.termination_reason = f"cycles_exceeded (n={effective_n}, cycles={self.cycles_since_constraint})"
            return {
                "sentence_index": self.sentence_count - 1,
                "terminate": True,
                "reason": self.termination_reason,
                "cycles_since_constraint": self.cycles_since_constraint,
                "effective_n": effective_n,
            }

        # Secondary trigger: reflection streak + rising sentiment
        if (self.consecutive_non_constraints >= self.reflection_streak_limit
                and self._rising_sentiment()):
            self.terminated = True
            self.termination_reason = (
                f"reflection_streak (streak={self.consecutive_non_constraints}, "
                f"sentiment_trend={[round(s, 2) for s in self.sentiment_window[-3:]]})"
            )
            return {
                "sentence_index": self.sentence_count - 1,
                "terminate": True,
                "reason": self.termination_reason,
                "cycles_since_constraint": self.cycles_since_constraint,
                "effective_n": effective_n,
            }

        # Force terminate on extreme drift regardless of cycles
        if current_drift >= self.drift_force_terminate:
            self.terminated = True
            self.termination_reason = f"drift_force_terminate (drift={current_drift:.2f})"
            return {
                "sentence_index": self.sentence_count - 1,
                "terminate": True,
                "reason": self.termination_reason,
                "cycles_since_constraint": self.cycles_since_constraint,
                "effective_n": effective_n,
            }

        return {
            "sentence_index": self.sentence_count - 1,
            "terminate": False,
            "reason": None,
            "cycles_since_constraint": self.cycles_since_constraint,
            "effective_n": effective_n,
        }

    def reset(self):
        self.cycles_since_constraint = 0
        self.total_constraints = 0
        self.sentence_count = 0
        self.token_count = 0
        self.consecutive_non_constraints = 0
        self.sentiment_window = []
        self.last_constraint_index = -1
        self.terminated = False
        self.termination_reason = None
