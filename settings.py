# /*******************************************************************************
# /
# /      filename:  settings.py
# /
# /   description:  Holds the static variables for the OS
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

from os_queues import OSQueue
from queue import Queue

time = 0
time_queue = list()
cpu = Queue(1)
job_scheduling = OSQueue()
ready_queue = OSQueue(100)
secondary_queue = OSQueue(300)
io_queue = list()
io_inbound = OSQueue()
finished = list()
memory = 512
memory_avail = 512
cpu_from_second = False


def init():
    global time
    global time_queue
    global cpu
    global job_scheduling
    global ready_queue
    global secondary_queue
    global io_queue
    global io_inbound
    global finished
    global memory
    global memory_avail
    global cpu_from_second
