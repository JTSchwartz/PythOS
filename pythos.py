import commands
import settings
import heapq

# PythOS Global Variables
memory = 512
time_q = settings.time_queue()


# Interprets
def cmd_create(user_input):

    def add(argv): return commands.Add(argv)

    def completion(argv): return commands.Completion(argv)

    def display(argv): return commands.Completion(argv)

    def expiration(argv): return commands.Expiration(argv)

    def io(argv): return commands.IO(argv)

    def termination(argv): return commands.Termination(argv)

    _commands = {
        "A": add,
        "C": completion,
        "D": display,
        "E": expiration,
        "I": io,
        "T": termination,
    }

    return _commands[user_input[0]](user_input[2:])


def ready_up():

    if settings.job_scheduling.empty():
        return

    current = settings.job_scheduling[0]

    while current.mem < settings.memory_avail:
        settings.memory_avail -= current.mem
        settings.ready_queue.put(settings.job_scheduling.get())
        current.quantum = settings.ready_queue.quantum

        if current.time_left < 100:
            current.leave = current.time_left + settings.time
        else:
            current.leave = 100 + settings.time

        heapq.heappush(time_q, (current.leave, current))
        current = settings.job_scheduling[0]


def cpu_next():

    if not settings.ready_queue.empty():
        commands.current_job = settings.ready_queue[0].get()
        settings.cpu.put(commands.current_job)
        commands.current_job.run()
    else:
        commands.current_job = settings.secondary_queue[0].get()
        settings.cpu.put(commands.current_job)
        commands.current_job.run()


if __name__ == '__main__':
    settings.init()

    while True:
        try:
            cmd = cmd_create(input())

            while time_q.count() != 0 and time_q[0][0] < cmd.start:
                settings.time = time_q[0][0]
                run_now = heapq.heappop(time_q)

                if settings.time == time_q[0][0] and time_q[0][1].internal and not run_now.internal:
                    heapq.heappop(time_q).run()
                    heapq.heappush(time_q, (settings.time, run_now))
                else:
                    run_now.run()  # TODO: Create run functions

            settings.time = cmd.start
            cmd.start_job()

            if cmd.command_type is 'I':
                time_q.remove(commands.current_job)
                heapq.heappush(time_q, (commands.current_job.leave, commands.current_job))
                commands.current_job.state = 4
                cpu_next()

            ready_up()

        except EOFError:  # TODO: Finish all jobs in the system
            break
