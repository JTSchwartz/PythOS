import commands
import settings
import heapq


# Interprets
def cmd_create(user_input):

    def add(argv): return commands.Add(argv)

    def completion(argv): return commands.Completion(argv)

    def display(argv): return commands.Display(argv)

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

    while current.mem <= settings.memory_avail:
        settings.memory_avail -= current.mem
        settings.ready_queue.put(settings.job_scheduling.get())
        current.quantum = settings.ready_queue.quantum
        current.state = 1

        if settings.job_scheduling.empty():
            break

        current = settings.job_scheduling[0]

    if settings.cpu.empty():
        cpu_next()


def cpu_next():

    if not settings.ready_queue.empty():
        commands.current_job = settings.ready_queue.get()
        settings.cpu.put(commands.current_job)
        commands.current_job.run()
    elif not settings.secondary_queue.empty():
        commands.current_job = settings.secondary_queue.get()
        settings.cpu.put(commands.current_job)
        commands.current_job.run()


if __name__ == '__main__':
    settings.init()

    while True:
        try:
            cmd = cmd_create(input())

            while len(settings.time_queue) != 0 and settings.time_queue[0][0] <= cmd.start:
                settings.time = settings.time_queue[0][0]
                run_now = heapq.heappop(settings.time_queue)[1]
                # run_now.run()

                if len(settings.time_queue) != 0 and settings.time == settings.time_queue[0][0]:
                    heapq.heappop(settings.time_queue)[1].run()
                    heapq.heappush(settings.time_queue, (settings.time, run_now))
                else:
                    run_now.run()

            settings.time = cmd.start
            cmd.start_job()
            ready_up()

        except EOFError:  # TODO: Finish all jobs in the system
            while len(settings.time_queue) != 0:
                settings.time = settings.time_queue[0][0]
                heapq.heappop(settings.time_queue)[1].run()

            print(
                "\nThe contents of the FINAL FINISHED LIST",
                "---------------------------------------\n",
                "Job #  Arr. Time  Mem. Req.  Run Time  Start Time  Com. Time",
                "-----  ---------  ---------  --------  ----------  ---------\n",
                sep="\n")

            count = wait_total = turnaround_total = 0.0

            for job in settings.finished:
                count += 1
                wait_total += job.hit - job.start
                turnaround_total += job.leave - job.start
                job.finished_print()

            print("\nThe Average Turnaround Time for the simulation was {} units.\n".format(turnaround_total/count))
            print("The Average Job Scheduling Wait Time for the simulation was {} units.\n".format((wait_total/count) - (2 * count)))
            print("There are {} blocks of main memory available in the system.".format(settings.memory_avail))

            break
