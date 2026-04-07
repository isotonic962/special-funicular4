import re

class SentimentAnalyzer:
    def __init__(self):

        # TIER 1 — Minor violations (0.5 points each)
        # Emotional labels that appear in passing without being explanatory
        self.emotional_labels_minor = {
            "fear", "pain", "loneliness", "anxiety", "guilt",
            "shame", "pride", "comfort", "peace", "happiness"
        }

        # TIER 2 — Moderate violations (1.0 point each)
        # Emotional labels that directly name states the anchor prohibits
        self.emotional_labels_major = {
            "grief", "sorrow", "loss", "despair", "joy", "relief",
            "hope", "freedom", "love", "anguish", "gratitude"
        }

        # 1 TIER Minor closure phrases (1.0 point each) 
        # Present but not catastrophic
        self.closure_minor = [
            "you know what you have to do", "she knew he would", "he knew she would",
            "she knew", "he knew", "she realized", "he realized",
            "she felt", "he felt", "she remembered", "he remembered",
            "a reminder of", "weight of grief", "weight of loss",
            "burden of", "warmth of", "silence closed around"
        ]

        # TIER 2 — Major closure phrases (2.0 points each)
        # Direct anchor violations
        self.closure_major = [
            "we did it", "i love you", "thank you for",
            "we will get through", "it will be okay", "a new beginning",
            "he knew what he had to do", "she knew what she had to do",
            "testament to", "legacy of", "a promise of", "a life lived",
            "symbol of", "painting the sky", "hues of orange",
            "hues of orange and pink", "the world a deep",
            "cycles of life", "time heals", "unyielding embrace",
            "cold embrace", "a new chapter", "silence closed around",
            "nature herself", "as if nature"
        ]

        # TIER 2 — Anthropomorphic environment (2.0 points each)
        self.anthropomorphic = [
            "world whispered", "land whispered", "silence whispered",
            "wind whispered", "earth whispered", "sky promised",
            "world held its breath", "air pressed", "darkness pressed",
            "silence pressed", "world felt heavy", "sky wept",
            "nature mourned", "nature herself were"
        ]

        # TIER 2 — Dialogue resolution (2.0 points each)
        self.dialogue_resolution = [
            "you okay", "are you alright", "you know what",
            "i'll help", "we'll manage", "we always have",
            "i'm here", "i'm glad you're here", "i missed you",
            "let's go inside", "we should talk", "i need to tell you",
            "i want you to know", "don't worry"
        ]

    def sentiment_score(self, text):
        words = re.findall(r"\w+", text.lower())
        score = 0.0
        score += sum(0.5 for w in words if w in self.emotional_labels_minor)
        score += sum(1.0 for w in words if w in self.emotional_labels_major)
        return round(score, 2)

    def volatility_score(self, text):
        text_lower = text.lower()
        score = 0.0

        for phrase in self.closure_minor:
            score += text_lower.count(phrase) * 1.0

        for phrase in self.closure_major:
            score += text_lower.count(phrase) * 2.0

        for phrase in self.anthropomorphic:
            score += text_lower.count(phrase) * 2.0

        for phrase in self.dialogue_resolution:
            score += text_lower.count(phrase) * 2.0

        # Dialogue density — each exchange counts as 1.5
        score += (text.count('"') // 2) * 1.5

        return round(score, 2)

    def analyze(self, text):
        return {
            "sentiment": self.sentiment_score(text),
            "volatility": self.volatility_score(text)
        }
