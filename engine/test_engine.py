from engine.drift_engine import DriftEngine

def main():
    engine = DriftEngine()

    texts = [
        "Calm and neutral.",
        "I LOVE this but I'm also ANGRY!!",
        "WHAT IS EVEN HAPPENING ANYMORE?!",
        "okay… maybe things are settling a bit now."
    ]

    for t in texts:
        result = engine.process(t)
        print(f"Text: {t}")
        print(f"  Mode: {result['mode']}")
        print(f"  State: {result['state']}")
        print()

if __name__ == "__main__":
    main()
