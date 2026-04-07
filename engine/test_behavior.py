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
        result = engine.process(
            text=t,
            response_text=(
                "This is the engine's full intended response before modulation. "
                "It contains multiple sentences so the behavior controller can adjust it."
            )
        )

        print(f"Input: {t}")
        print(f"Mode: {result['mode']}")
        print(f"Output: {result['response']}")
        print()

if __name__ == "__main__":
    main()


