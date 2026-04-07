from engine.drift_engine import DriftEngine

def main():
    engine = DriftEngine()

    # Spike the system
    spike = "WHAT IS EVEN HAPPENING ANYMORE?!"
    for _ in range(3):
        engine.process(spike, "Response.")

    # Now feed calm messages and watch recovery
    for i in range(5):
        result = engine.process("Calm and neutral.", "Response.")
        print(f"Step {i}: state={result['state']}, mode={result['mode']}")

if __name__ == "__main__":
    main()
