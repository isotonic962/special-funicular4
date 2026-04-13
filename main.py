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
    from engine.texture import TextureAnalyzer
    _tex = TextureAnalyzer().analyze(output, user_input)
    print(f'  [TEXTURE] fig={_tex["figurative_density"]} act={_tex["action_pct"]} int={_tex["interiority_pct"]} dial={_tex["dialogue_density"]} rhythm={_tex["sentence_rhythm"]} echo={_tex["prompt_echo"]}')
