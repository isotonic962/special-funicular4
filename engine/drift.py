class DriftScorer:
    def __init__(self, w_sentiment=0.0, w_volatility=0.0, w_entropy=0.5):
        self.w_sentiment = w_sentiment
        self.w_volatility = w_volatility
        self.w_entropy = w_entropy

    def score(self, analysis):
        """
        analysis is the dict returned by DriftAnalyzer.analyze(text)
        {
            "sentiment": ...,
            "volatility": ...,
            "entropy": ...
        }
        """

        s = analysis["sentiment"]
        v = analysis["volatility"]
        e = analysis["entropy"]

        # Normalize sentiment: negative sentiment increases drift
        sentiment_component = s * self.w_sentiment

        # Volatility is directly destabilizing
        volatility_component = v * self.w_volatility

        # Entropy increases drift as language becomes more chaotic
        entropy_component = e * self.w_entropy

        drift = max(0.0, sentiment_component + volatility_component + entropy_component)

        return {
            "sentiment_component": sentiment_component,
            "volatility_component": volatility_component,
            "entropy_component": entropy_component,
            "drift_score": drift
        }
