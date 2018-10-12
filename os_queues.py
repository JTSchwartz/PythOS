from queue import Queue


class OSQueue(Queue):

    time_limit: int

    def __init__(self, time_limit=None):
        super().__init__()
        self.time_limit = time_limit
