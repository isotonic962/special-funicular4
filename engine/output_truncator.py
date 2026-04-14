import re
from .constraint_detector import ConstraintDetector
from .cycle_counter import CycleCounter
from .sentiment import SentimentAnalyzer


class OutputTruncator:
    """
    Post-generation truncation system.

    Splits model output into sentences, runs constraint detection and
    cycle counting, and cuts at the last clean constraint sentence
    when termination triggers.
    """

    def __init__(self, base_n=2, min_tokens=120):
        self.detector = ConstraintDetector()
        self.sentiment = SentimentAnalyzer()
        self.base_n = base_n
        self.min_tokens = min_tokens

    def _split_sentences(self, text):
        """
        Split text into sentences. Handles common abbreviations
        and dialogue punctuation.
        """
        # Split on sentence-ending punctuation followed by space or newline
        # Preserve paragraph breaks as empty entries for reconstruction
        protected = re.sub(r'\b(Mr|Mrs|Ms|Dr|St|Jr|Sr|Prof)[.]\s', lambda m: m.group().replace('. ', '__ABBR__'), text)
        raw = re.split(r'(?<=[.!?])\s+(?=[A-Z])', protected)
        sentences = [s.replace('__ABBR__', '. ').strip() for s in raw if s.strip()]
        return sentences

    def _per_sentence_sentiment(self, sentence):
        """Get sentiment score for a single sentence using existing scorer."""
        return self.sentiment.sentiment_score(sentence)

    def _per_sentence_volatility(self, sentence):
        """Get volatility score for a single sentence."""
        return self.sentiment.volatility_score(sentence)

    def _find_cut_point(self, sentences, scan_results, trigger_index):
        """
        Walk back from the trigger index to find the best cut point.
        The cut point is the last sentence that:
        1. Was a constraint (is_constraint=True, confidence >= 0.5), OR
        2. Had below-average volatility for the generation

        Returns the index (inclusive) of the last sentence to keep.
        """
        # Calculate average volatility across all sentences up to trigger
        vols = [self._per_sentence_volatility(s) for s in sentences[:trigger_index + 1]]
        avg_vol = sum(vols) / len(vols) if vols else 0.0

        # Walk back from trigger
        for i in range(trigger_index, -1, -1):
            result = scan_results[i]
            # Only stop on a real constraint
            if result["is_constraint"] and result["confidence"] >= 0.5:
                return i

        # No constraint found — walk back to last non-narration, non-reflection sentence
        # with below-average volatility (but not the trigger itself)
        for i in range(trigger_index - 1, -1, -1):
            result = scan_results[i]
            if result["verb_class"] not in ("narration", "reflection") and vols[i] <= avg_vol:
                return i

        # Hard fallback: cut at trigger minus 1 to always remove something
        return max(0, trigger_index - 1)

    def truncate(self, full_text, current_volatility=0.0, current_drift=0.0):
        """
        Run the full truncation pipeline on model output.

        Args:
            full_text: raw model output string
            current_volatility: from drift engine (for N modifier)
            current_drift: from drift engine (for force terminate)

        Returns:
        {
            "text": truncated string,
            "original_text": full original string,
            "sentences_total": int,
            "sentences_kept": int,
            "sentences_removed": int,
            "cut_index": int or None,
            "trigger_index": int or None,
            "termination_reason": str or None,
            "was_truncated": bool,
            "scan_log": list of per-sentence scan results
        }
        """
        # Strip markdown artifacts (bold headers, section labels)
        clean_text = re.sub(r'#{1,6}\s*[^\n]+\n?', '', full_text)
        clean_text = re.sub(r'\*\*[^*]+\*\*', '', clean_text)
        clean_text = re.sub(r'\n{2,}', ' ', clean_text)
        clean_text = re.sub(r'\s{2,}', ' ', clean_text).strip()
        full_text = clean_text

        sentences = self._split_sentences(full_text)

        if not sentences:
            return {
                "text": full_text,
                "original_text": full_text,
                "sentences_total": 0,
                "sentences_kept": 0,
                "sentences_removed": 0,
                "cut_index": None,
                "trigger_index": None,
                "termination_reason": None,
                "was_truncated": False,
                "scan_log": [],
            }

        counter = CycleCounter(base_n=self.base_n, min_tokens=self.min_tokens)
        scan_results = []
        trigger_index = None

        for i, sentence in enumerate(sentences):
            # Detect constraint vs non-constraint
            scan = self.detector.scan(sentence)
            scan_results.append(scan)

            # Per-sentence sentiment for the rising-sentiment trigger
            sent_score = self._per_sentence_sentiment(sentence)

            # Update cycle counter
            result = counter.update(
                constraint_result=scan,
                sentence=sentence,
                sentence_sentiment=sent_score,
                current_volatility=current_volatility,
                current_drift=current_drift,
            )

            if result["terminate"]:
                trigger_index = i
                break

        # No termination triggered — return full text
        if trigger_index is None:
            return {
                "text": full_text,
                "original_text": full_text,
                "sentences_total": len(sentences),
                "sentences_kept": len(sentences),
                "sentences_removed": 0,
                "cut_index": None,
                "trigger_index": None,
                "termination_reason": None,
                "was_truncated": False,
                "scan_log": scan_results,
            }

        # Find clean cut point
        cut_index = self._find_cut_point(sentences, scan_results, trigger_index)
        kept = sentences[: cut_index + 1]
        truncated_text = " ".join(kept)

        return {
            "text": truncated_text,
            "original_text": full_text,
            "sentences_total": len(sentences),
            "sentences_kept": cut_index + 1,
            "sentences_removed": len(sentences) - (cut_index + 1),
            "cut_index": cut_index,
            "trigger_index": trigger_index,
            "termination_reason": counter.termination_reason,
            "was_truncated": True,
            "scan_log": scan_results,
        }
