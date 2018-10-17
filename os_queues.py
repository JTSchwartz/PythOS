# /*******************************************************************************
# /
# /      filename:  os_queues.py
# /
# /   description:  Added functionality for Python Queues
# /
# /        author:  Schwartz, Jacob
# /      login id:  FA_18_CPS356_33
# /
# /         class:  CPS 356
# /    instructor:  Perugini
# /    assignment:  Midterm Project
# /
# /      assigned:  September 27, 2018
# /           due:  October 25, 2018
# /
# /******************************************************************************/

from collections import deque


class OSQueue(deque):
    quantum = None

    def __init__(self, quantum=None):
        super().__init__()
        self.quantum = quantum

    def put(self, obj):
        self.append(obj)

    def put_back(self, obj):
        self.appendleft(obj)

    def get(self):
        return self.popleft()

    def empty(self):
        return len(self) == 0
