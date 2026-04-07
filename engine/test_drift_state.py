from engine.analyze import DriftAnalyzer
from engine.drift import DriftScorer
from engine.drift_state import DriftState

def main():
    analyzer = DriftAnalyzer()
    scorer = DriftScorer()
    state = DriftState(alpha=0.3)

    texts = [
        "Calm, neutral, nothing much happening.",
        "I LOVE this but I'm also ANGRY!!",
        "WHAT IS EVEN GOING ON ANYMORE?!",
    ]

    for t in texts:
        analysis = analyzer.analyze(t)
        drift = scorer.score(analysis)["drift_score"]
        smoothed = state.update(drift)
        print(f"Text: {t}")
        print(f"  raw drift: {drift}")
        print(f"  smoothed drift state: {smoothed}")
        print()

if __name__ == "__main__":
    main()
