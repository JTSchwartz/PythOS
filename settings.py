from os_queues import OSQueue

job_scheduling = OSQueue()
ready_queue = OSQueue(100)
secondary_queue = OSQueue(300)
io_queue = OSQueue()
finished = list()
memory = 512


def init():
    global job_scheduling
    global ready_queue
    global secondary_queue
    global io_queue
    global memory
    global finished

    # job_scheduling = OSQueue()
    # ready_queue = OSQueue(100)
    # secondary_queue = OSQueue(300)
    # io_queue = OSQueue()
    # memory = 512
