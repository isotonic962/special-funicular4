import subprocess
import json

def generate(prompt, temperature=0.7, top_p=0.9):
    cmd = [
        "./main",
        "-m", "downloads/qwen2.5-3b-instruct/qwen2.5-3b-instruct-q4_k_m.gguf",
        "--temp", str(temperature),
        "--top-p", str(top_p),
        "-p", prompt
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()

    return output
