from engine.controller import run_drift_pipeline

with open("engine/prompts/system_anchor.txt", "r") as f:
    ANCHOR_TEXT = f.read()

while True:
    user_input = input("You: ")
    if not user_input.strip():
        print("(empty input skipped)")
        continue
    output = run_drift_pipeline(user_input, ANCHOR_TEXT)
    print("Engine:", output)
