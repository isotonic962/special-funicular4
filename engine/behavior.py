import random

class BehaviorController:
    def __init__(self):
        pass

    def respond(self, mode, text):
        if mode == "stable":
            return self._stable(text)
        elif mode == "unstable":
            return self._unstable(text)
        elif mode == "critical":
            return self._critical(text)
        return text

    def _stable(self, text):
        return text

    def _unstable(self, text):
        return text



    def _critical(self, text):
        return text



