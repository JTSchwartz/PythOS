from queue import Queue


class OSQueue(Queue):

    quantum: int

    def __init__(self, quantum=None):
        super().__init__()
        self.quantum = quantum
