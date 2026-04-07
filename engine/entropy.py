import math
import re
from collections import Counter

class EntropyCalculator:
    def __init__(self):
        pass

    def tokenize(self, text):
        return re.findall(r"\w+", text.lower())

    def shannon_entropy(self, text):
        tokens = self.tokenize(text)
        if not tokens:
            return 0.0

        counts = Counter(tokens)
        total = sum(counts.values())

        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)

        return entropy

    def analyze(self, text):
        return {
            "entropy": self.shannon_entropy(text)
        }
