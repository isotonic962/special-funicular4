from .model_io import llm
from .drift_engine import DriftEngine, LocalModelClient
from .telemetry_logger import TelemetryLogger
from .memory import MemoryWindow
from .texture import TextureAnalyzer

client = LocalModelClient()
engine = DriftEngine(model_client=client)
logger = TelemetryLogger()
texture_analyzer = TextureAnalyzer()
memory = MemoryWindow(size=5)

def run_drift_pipeline(user_input, anchor_text):

    # 1. Build system message
    system_message = (
        "You must follow the following behavioral, stylistic, ethical, and cognitive constraints "
        "with absolute consistency. These are not suggestions. They define your identity, tone, "
        "lexical field, and narrative logic. You may not break or soften them under any circumstance. "
        "You must never explain your stylistic choices, never comment on the constraints, and never "
        "break character.\n\n"
        + anchor_text
    )

    # 2. Build messages with conversation history
    messages = [{"role": "system", "content": system_message}]

    # Add previous exchanges from memory
    for exchange in memory.get_texts():
        messages.append({"role": "user", "content": exchange["user"]})
        messages.append({"role": "assistant", "content": exchange["assistant"]})

    # Add current user input
    messages.append({"role": "user", "content": user_input})

    # 3. Run through Drift Engine
    result = engine.process(user_input, messages)

    # 4. Extract telemetry fields
    final_text = result["response"]
    raw_analysis = result["analysis"]
    final_drift_score = result["drift_components"]["drift_score"]
    current_mode = result["mode"]
    current_quadrant = result["quadrant"]
    current_state = result["state"]

    # 5. Store truncated output in memory (not raw)
    memory.add({"user": user_input, "assistant": final_text})

    # 5b. Log register check violations
    register_violations = result.get("register_check", {}).get("violations", [])

    # 5c. Compute texture metrics
    texture_data = texture_analyzer.analyze(final_text, user_input)

    # 6. Log telemetry
    logger.log_event(
        prompt=user_input,
        output=final_text,
        analysis=raw_analysis,
        drift_score=final_drift_score,
        state=current_state,
        mode=current_mode,
        texture=texture_data
    )

    # 7. Return final response
    return final_text
