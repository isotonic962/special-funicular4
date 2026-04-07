from engine.analyze import DriftAnalyzer
from engine.drift import DriftScorer

def main():
    analyzer = DriftAnalyzer()
    scorer = DriftScorer()

    text = "I LOVE this but I'm also ANGRY!! Chaos rising."
    analysis = analyzer.analyze(text)
    drift = scorer.score(analysis)

    print("Analysis:", analysis)
    print("Drift:", drift)

if __name__ == "__main__":
    main()
