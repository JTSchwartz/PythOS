import commands
import settings
from os_queues import OSQueue
import heapq

# PythOS Global Variables
memory = 512
time_q = settings.time_queue()


# Interprets
def cmd_create(user_input):

    def add(argv):
        return commands.Add(argv)

    def completion(argv):
        return commands.Completion(argv)

    def display(argv):
        return commands.Completion(argv)

    def expiration(argv):
        return commands.Expiration(argv)

    def io(argv):
        return commands.IO(argv)

    def termination(argv):
        return commands.Termination(argv)

    _commands = {
        "A": add,
        "C": completion,
        "D": display,
        "E": expiration,
        "I": io,
        "T": termination,
    }

    return _commands[user_input[0]](user_input[2:])


def create_queues():
    return OSQueue(100), OSQueue(300), OSQueue()


def transition(q1, q2):

    current = q1[0]

    if current.mem < settings.memory_avail:
        settings.memory_avail -= current.mem
        q2.put(q1.get())
        current.quantum = q2.quantum

        if current.time_left < q2.quantum:
            current.leave = current.time_left + settings.time
        else:
            current.leave = q2.quantum + settings.time

        heapq.heappush(time_q, (current.leave, current))


if __name__ == '__main__':  # TODO: Create time

    settings.init()
    js_q = settings.job_scheduling
    ready_q = settings.ready_queue
    sec_q = settings.secondary_queue

    while True:
        try:
            cmd = cmd_create(input())

            while time_q.count() != 0 and time_q[0][1].leave < cmd.start:
                run_now = heapq.heappop(time_q)

                if run_now.leave == time_q[0][0] and time_q[0][1].internal:
                    temp = run_now
                    run_now = heapq.heappop(time_q)
                    heapq.heappush(time_q, (run_now.leave, run_now))

                settings.time = run_now.queue_arrival
                run_now.run()

            settings.time = cmd.start
            cmd.start()

            if cmd.command_type is 'I':
                time_q.remove(commands.current_job)
                heapq.heappush(time_q, (commands.current_job.leave, commands.current_job))
            if cmd.command_type is not 'A':
                continue

        except EOFError:  # TODO: Finish all jobs in the system
            break
