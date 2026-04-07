from .sentiment import SentimentAnalyzer
from .entropy import EntropyCalculator

class DriftAnalyzer:
    def __init__(self):
        self.sentiment = SentimentAnalyzer()
        self.entropy = EntropyCalculator()

    def analyze(self, text):
        s = self.sentiment.analyze(text)
        e = self.entropy.analyze(text)

        return {
            "sentiment": s["sentiment"],
            "volatility": s["volatility"],
            "entropy": e["entropy"]
        }
