import re


class ConstraintDetector:
    """
    Classifies sentences as constraints (situation changes) or non-constraints
    (interiority, meaning-making, reflection).

    A constraint is a sentence where the subject changes what it's doing
    or something external changes the conditions.
    """

    def __init__(self):
        # Physical/transitional verbs — indicate situation change
        self.constraint_verbs = {
            "turned", "stopped", "set", "stood", "crossed", "lifted",
            "lowered", "opened", "closed", "entered", "left", "dropped",
            "picked", "pulled", "pushed", "cut", "broke", "struck",
            "placed", "carried", "threw", "caught", "dug", "poured",
            "split", "dragged", "loaded", "unloaded", "hitched",
            "saddled", "mounted", "dismounted", "knelt", "rose",
            "crouched", "leaned", "reached", "gripped", "released",
            "swung", "hammered", "nailed", "sawed", "chopped",
            "slipped", "stumbled", "fell", "climbed", "stepped",
            "walked", "ran", "moved", "shifted", "slid",
            "lit", "doused", "ate", "drank", "spat", "coughed",
            "dressed", "undressed", "washed", "wiped", "scraped",
            "folded", "unfolded", "packed", "unpacked", "locked",
            "unlocked", "bolted", "fastened", "unfastened",
            "began", "finished", "started", "ended", "halted",
            "paused", "resumed", "continued",
            "plowed", "ploughed", "sowed", "harvested", "reaped",
            "threshed", "harrowed", "seeded", "mowed", "scythed",
            "buried", "dug", "filled", "covered", "laid", "lowered",
            "signed", "handed", "sold", "paid", "received",
        }

        # Environmental transition markers
        self.env_transitions = [
            "darkened", "brightened", "froze", "thawed",
            "snow began", "rain began", "wind rose", "wind died",
            "sun broke", "sun set", "light fell", "light faded",
            "door opened", "door closed", "fire caught", "fire died",
            "sound arrived", "sound stopped", "bell rang", "clock struck",
            "ice cracked", "branch snapped", "thunder rolled",
            "temperature dropped", "fog rolled", "clouds gathered",
        ]

        # Interiority / reflection verbs — model sliding into meaning-making
        self.reflection_verbs = {
            "remembered", "recalled", "thought", "wondered",
            "realized", "understood", "knew", "felt",
            "imagined", "wished", "hoped", "feared",
            "believed", "supposed", "considered", "reflected",
            "mourned", "grieved", "longed", "missed",
        }

        # Narrator interpretation pattern:
        # [subject] + [seemed/felt/appeared/held/carried] + [qualifier]
        self.narrator_verbs = {
            "seemed", "appeared", "felt", "held", "carried",
            "bore", "suggested", "implied", "betrayed",
            "radiated", "emanated", "exuded",
        }

        # Copula + temporal finality — state summary detection
        # "he was gone now", "she was alone forever"
        self.finality_markers = {
            "now", "forever", "never", "always", "at last",
            "once more", "no more", "for good", "finally",
            "already", "too late", "no longer",
        }

        # Meaning-making qualifiers after narrator verbs
        self.meaning_qualifiers = [
            "more than", "almost", "as if", "as though",
            "somehow", "something", "whatever", "anything",
            "nothing", "everything", "too great", "too heavy",
            "too much", "beyond", "beneath the surface",
        ]

    def _tokenize(self, sentence):
        return re.findall(r"\w+", sentence.lower())

    def _has_constraint_verb(self, tokens):
        return any(t in self.constraint_verbs for t in tokens)

    def _has_env_transition(self, sentence):
        s = sentence.lower()
        return any(phrase in s for phrase in self.env_transitions)

    def _has_reflection_verb(self, tokens):
        return any(t in self.reflection_verbs for t in tokens)

    def _has_narrator_interpretation(self, sentence):
        """
        Detects structural meaning-making:
        - narrator verbs + meaning qualifiers
        - copula + finality markers
        """
        s = sentence.lower()
        tokens = self._tokenize(sentence)

        # Pattern 1: narrator verb + qualifier
        has_narrator_verb = any(t in self.narrator_verbs for t in tokens)
        has_qualifier = any(q in s for q in self.meaning_qualifiers)
        if has_narrator_verb and has_qualifier:
            return True

        # Pattern 2: copula (was/were/is) + finality
        copulas = {"was", "were", "is", "had been", "would be"}
        has_copula = any(c in s for c in copulas)
        has_finality = any(t in self.finality_markers for t in tokens)
        if has_copula and has_finality:
            return True

        return False

    def _has_emotional_labeling(self, sentence):
        """
        Catches emotional state naming that bypasses the lexical scorer.
        Looks for 'felt [adjective]' and 'heart [verb]' patterns.
        """
        s = sentence.lower()
        # "felt altered", "felt heavy", "felt nothing", "felt empty"
        if re.search(r"\bfelt\s+\w+", s):
            return True
        # "heart clenched", "heart sank", "heart pounded"
        if re.search(r"\bheart\s+(clenched|sank|pounded|ached|broke|tightened|raced|stopped)", s):
            return True
        return False

    def scan(self, sentence):
        """
        Returns classification for a single sentence.

        {
            "is_constraint": bool,
            "verb_class": "physical" | "environmental" | "reflection" | "narration" | "neutral",
            "confidence": float (0-1),
            "flags": list of triggered detectors
        }
        """
        tokens = self._tokenize(sentence)
        flags = []

        has_physical = self._has_constraint_verb(tokens)
        has_env = self._has_env_transition(sentence)
        has_reflection = self._has_reflection_verb(tokens)
        has_narration = self._has_narrator_interpretation(sentence)
        has_emotional = self._has_emotional_labeling(sentence)

        if has_physical:
            flags.append("physical_verb")
        if has_env:
            flags.append("env_transition")
        if has_reflection:
            flags.append("reflection_verb")
        if has_narration:
            flags.append("narrator_interpretation")
        if has_emotional:
            flags.append("emotional_labeling")

        # Decision logic:
        # A sentence with a physical verb or env transition IS a constraint,
        # UNLESS it also has narrator interpretation (meaning the physical
        # action is being used as a vehicle for meaning-making).
        # e.g. "He stepped forward as if carrying the weight of the world"

        if has_narration or has_emotional:
            # Narrator interpretation overrides physical verb
            # unless the physical action is the main clause
            if has_physical and not has_reflection:
                # Physical verb present but tainted by narration
                # Lower confidence constraint
                return {
                    "is_constraint": True,
                    "verb_class": "physical",
                    "confidence": 0.4,
                    "flags": flags,
                }
            return {
                "is_constraint": False,
                "verb_class": "narration" if has_narration else "reflection",
                "confidence": 0.8,
                "flags": flags,
            }

        if has_reflection and not has_physical:
            return {
                "is_constraint": False,
                "verb_class": "reflection",
                "confidence": 0.7,
                "flags": flags,
            }

        if has_physical or has_env:
            return {
                "is_constraint": True,
                "verb_class": "physical" if has_physical else "environmental",
                "confidence": 0.8,
                "flags": flags,
            }

        # Neutral — no strong signal either way
        return {
            "is_constraint": False,
            "verb_class": "neutral",
            "confidence": 0.3,
            "flags": flags,
        }
