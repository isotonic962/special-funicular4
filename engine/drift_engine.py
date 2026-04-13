import requests
from .analyze import DriftAnalyzer
from .drift import DriftScorer
from .drift_state import DriftState
from .drift_modes import DriftModeClassifier
from .behavior import BehaviorController
from .quadrant import QuadrantClassifier
from .rolling_baseline import RollingBaseline
from .recovery import DriftRecovery
from .output_truncator import OutputTruncator
from .texture import TextureAnalyzer


class LocalModelClient:
    def __init__(self, base_url="http://127.0.0.1:8080/v1", model="qwen2.5-3b-instruct-q4_k_m"):
        self.base_url = base_url
        self.model = model

    def chat(self, messages, temperature=0.7, repeat_penalty=1.1):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "repeat_penalty": repeat_penalty
        }
        r = requests.post(f"{self.base_url}/chat/completions", json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


class DriftEngine:
    def __init__(self, model_client, alpha=0.3, stable_threshold=12, critical_threshold=20,
                 truncation_n=2, truncation_min_tokens=120):
        self.model = model_client
        self.analyzer = DriftAnalyzer()
        self.scorer = DriftScorer()
        self.state = DriftState(alpha=alpha)
        self.classifier = DriftModeClassifier(
            stable_threshold=stable_threshold,
            critical_threshold=critical_threshold
        )
        self.behavior = BehaviorController()
        self.recovery = DriftRecovery(anchor=0.0, decay=0.05)
        self.quadrant = QuadrantClassifier()
        self.baseline = RollingBaseline()
        self.texture = TextureAnalyzer()
        self.truncator = OutputTruncator(base_n=truncation_n, min_tokens=truncation_min_tokens)

    def process(self, text, messages=None):
        # 1. Generate raw model response
        if messages is None:
            messages = [{"role": "user", "content": text}]
        params, action, avg_vol, avg_ent = self.baseline.recommend()
        response_text = self.model.chat(messages, **params)

        # 2. Pre-truncation: get previous-turn volatility/drift for N modifier
        #    Use rolling baseline averages as proxy for current state
        pre_vol = avg_vol if avg_vol is not None else 0.0
        pre_drift = self.state.get_state()

        # 3. TRUNCATE before analysis
        trunc_result = self.truncator.truncate(
            response_text,
            current_volatility=pre_vol,
            current_drift=pre_drift
        )
        truncated_text = trunc_result["text"]

        reg_result = {"pass": True, "violations": [], "raw_response": "disabled"}

        # 4. Analyze the truncated text (not the raw output)
        analysis = self.analyzer.analyze(truncated_text)

        # 5. Compute drift score
        drift_info = self.scorer.score(analysis)
        drift_score = drift_info["drift_score"]

        # 6a. Update temporal drift state
        state_value = self.state.update(drift_score)

        # 6b. Apply recovery toward anchor
        state_value = self.recovery.apply(state_value)

        # 7. Classify mode (stable / unstable / critical)
        mode = self.classifier.classify(drift_score)
        quadrant = self.quadrant.classify(analysis["volatility"], analysis["entropy"])

        # 8. Apply behavioral modulation on truncated text
        modulated = self.behavior.respond(mode, truncated_text)

        # 9. Return structured engine output
        return {
            "analysis": analysis,
            "drift_components": drift_info,
            "state": state_value,
            "mode": mode,
            "raw_response": response_text,
            "response": modulated,
            "quadrant": quadrant,
            "baseline_action": action,
            "register_check": reg_result,
            "truncation": {
                "was_truncated": trunc_result["was_truncated"],
                "sentences_total": trunc_result["sentences_total"],
                "sentences_kept": trunc_result["sentences_kept"],
                "sentences_removed": trunc_result["sentences_removed"],
                "termination_reason": trunc_result["termination_reason"],
                "cut_index": trunc_result["cut_index"],
                "scan_log": trunc_result["scan_log"],
            }
        }


# ---------------------------------------------------------
# REPL
# ---------------------------------------------------------

if __name__ == "__main__":
    model_client = LocalModelClient(
        base_url="http://127.0.0.1:8080/v1",
        model="qwen2.5-3b-instruct-q4_k_m"
    )

    engine = DriftEngine(model_client=model_client)

    result = engine.process("Hello there")
    print(result["response"])

    while True:
        user_input = input("> ")
        if user_input.strip().lower() in ["exit", "quit"]:
            break

        result = engine.process(user_input)
        print(result["response"])
        from engine.texture import TextureAnalyzer as _TA
        _tex = _TA().analyze(result["response"], user_input)
        print(f'  [TEXTURE] fig={_tex["figurative_density"]} act={_tex["action_pct"]} int={_tex["interiority_pct"]} dial={_tex["dialogue_density"]} rhythm={_tex["sentence_rhythm"]} echo={_tex["prompt_echo"]}')
        if result.get("register_check") and not result["register_check"]["pass"]:
            print(f"  [REGISTER] violations={result['register_check']['violations']}")
        if result["truncation"]["was_truncated"]:
            t = result["truncation"]
            print(f"\n  [TRUNCATED] {t['sentences_kept']}/{t['sentences_total']} sentences kept")
            print(f"  [REASON] {t['termination_reason']}")
            for i, s in enumerate(t['scan_log']):
                print(f"  [{i}] constraint={s['is_constraint']} class={s['verb_class']} conf={s['confidence']:.1f} flags={s['flags']}")

