from os_queues import OSQueue
from queue import PriorityQueue
from queue import Queue

time = 0
time_queue = list()
cpu = Queue(1)
job_scheduling = OSQueue()
ready_queue = OSQueue(100)
secondary_queue = OSQueue(300)
io_queue = PriorityQueue()
finished = list()
memory = 512
memory_avail = 512


def init():
    global time
    global time_queue
    global cpu
    global job_scheduling
    global ready_queue
    global secondary_queue
    global io_queue
    global finished
    global memory
    global memory_avail

    # job_scheduling = OSQueue()
    # ready_queue = OSQueue(100)
    # secondary_queue = OSQueue(300)
    # io_queue = OSQueue()
    # memory = 512
