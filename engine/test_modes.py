from engine.drift_modes import DriftModeClassifier

def main():
    classifier = DriftModeClassifier()

    samples = [1.3, 4.4, 8.2, 13.7]

    for s in samples:
        print(s, "→", classifier.classify(s))

if __name__ == "__main__":
    main()
