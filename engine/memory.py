class MemoryWindow:
    def __init__(self, size=5):
        self.size = size
        self.buffer = []

    def add(self, text):
        self.buffer.append(text)
        if len(self.buffer) > self.size:
            self.buffer.pop(0)

    def get_texts(self):
        return list(self.buffer)

    def clear(self):
        self.buffer = []
