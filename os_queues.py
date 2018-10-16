from collections import deque


class OSQueue(deque):

    quantum: int

    def __init__(self, quantum=None):
        super().__init__()
        self.quantum = quantum

    def put(self, obj):
        self.append(obj)

    def get(self):
        return self.popleft()

    def empty(self):
        return len(self) == 0
