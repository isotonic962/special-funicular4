import re


class RegisterCheck:
    """
    Post-truncation structural validation using the LLM itself.
    Catches genre drift, role fixity violations, and anchor breaches
    that sentence-level detection cannot.
    """

    def __init__(self, model_client):
        self.model = model_client

    def check(self, prompt, output):
        """
        Ask the model to evaluate its own output against the prompt constraints.

        Returns:
        {
            "pass": bool,
            "violations": list of str,
            "raw_response": str
        }
        """
        check_prompt = f"""You are a strict prose auditor. Given the PROMPT and the OUTPUT below, answer each question with YES or NO only. No explanation.

PROMPT: {prompt}

OUTPUT: {output}

1. Does the output contain character names not provided in the prompt?
2. Does the output introduce characters not specified or directly implied by the prompt?
3. Does the output contain dialogue from characters not present in the scene?
4. Does the output describe a setting or situation not implied by the prompt (e.g. auction, courtroom, ceremony)?
5. Does any sentence exist primarily to explain what an action means or how it should be interpreted?

Reply in this exact format:
1: YES or NO
2: YES or NO
3: YES or NO
4: YES or NO
5: YES or NO"""

        try:
            messages = [{"role": "user", "content": check_prompt}]
            raw = self.model.chat(messages, temperature=0.1, repeat_penalty=1.0)

            violations = []
            labels = {
                "1": "name_invention",
                "2": "role_fixity",
                "3": "absent_character_dialogue",
                "4": "genre_drift",
                "5": "meaning_making",
            }

            for line in raw.strip().split("\n"):
                line = line.strip()
                if ":" in line:
                    num = line.split(":")[0].strip()
                    answer = line.split(":")[1].strip().upper()
                    if num in labels and "YES" in answer:
                        violations.append(labels[num])

            if violations:
                print(f"  [REGISTER] violations={violations}")
            return {
                "pass": len(violations) == 0,
                "violations": violations,
                "raw_response": raw,
            }

        except Exception as e:
            # If the check fails, pass through — don't block generation
            return {
                "pass": True,
                "violations": [],
                "raw_response": f"ERROR: {str(e)}",
            }
