import settings
import heapq
import re

current_job = None


class Command:
    start = leave = mem = job_id = run_time = io = state = time_left = quantum = queue_arrival = time_on_cpu = hit = 0
    internal = been_to_cpu = False
    command_type: chr

    def __lt__(self, other):
        return not self.internal

    @staticmethod
    def cpu_next():
        global current_job

        if not settings.job_scheduling.empty():
            current = settings.job_scheduling[0]

            while current.mem <= settings.memory_avail:
                settings.memory_avail -= current.mem
                settings.ready_queue.put(settings.job_scheduling.get())
                current.quantum = settings.ready_queue.quantum
                current.state = 1

                if settings.job_scheduling.empty():
                    break

                current = settings.job_scheduling[0]

        if not settings.ready_queue.empty():
            current_job = settings.ready_queue.get()
            settings.cpu.put(current_job)
            current_job.run()
        elif not settings.secondary_queue.empty():
            current_job = settings.secondary_queue.get()
            settings.cpu.put(current_job)
            current_job.run()
        else:
            current_job = None


class Add(Command):
    trigger: Command = None

    def __init__(self, args):
        self.command_type = 'A'
        argv = re.split('\s+', args)
        self.start = int(argv[0])
        self.job_id = int(argv[1])
        self.mem = int(argv[2])
        self.run_time = self.time_left = int(argv[3])

    def start_job(self):
        print("Event: {}   Time: {}".format(self.command_type, self.start))

        if self.mem > settings.memory:
            print("This job exceeds the system's main memory capacity.")
            return

        settings.job_scheduling.put(self)

    def run(self):
        # STATES:
        # 0: JOB SCHEDULING TO READY
        # 1: READY 1 TO CPU
        # 2: CPU TO READY 2
        # 3: READY 2 TO CPU
        # 4: CPU TO IO WAIT
        # 5: IO WAIT TO READY 1
        # 6: JOB DONE

        def ready_cpu(this):

            if not this.been_to_cpu:
                this.been_to_cpu = True
                this.hit = settings.time

            move_to_cpu(this, 100)

        def secondary_cpu(this):
            move_to_cpu(this, 300)

        def move_to_cpu(this, n):
            global current_job

            if self in settings.time_queue:
                settings.time_queue.remove(self)
                heapq.heapify(settings.time_queue)

            this.quantum = n
            this.queue_arrival = settings.time
            current_job = this

            if this.time_left <= n:
                this.state = 6
                this.leave = settings.time + this.time_left
                this.trigger = Termination(this)
            else:
                this.state = 2
                this.leave = settings.time + this.quantum
                this.trigger = Expiration(this)

        def terminate(this):
            return

        _switcher = {
            1: ready_cpu,
            # 2: cpu_secondary,
            3: secondary_cpu,
            # 4: cpu_io,
            # 5: io_ready,
            6: terminate,
        }

        _switcher[self.state](self)

    def format_print(self):
        print("%5d%11d%11d%10d" % (self.job_id, self.start, self.mem, self.run_time))

    def print_on_cpu(self):
        print("\n%7d%12d%21d\n\n" % (self.job_id, self.hit, self.time_left - (settings.time - self.queue_arrival)))

    def finished_print(self):  # TODO: Finish Formatting for Finished List
        print("%5d%11d%11d%10d%12d%11d" % (self.job_id, self.start, self.mem, self.run_time, self.hit, self.leave))


class Completion(Command):

    def __init__(self, time):
        self.command_type = 'C'
        self.internal = True
        heapq.heappush(settings.time_queue, (time, self))

    @staticmethod
    def run():
        settings.ready_queue.put(settings.io_queue.get())


class Display(Command):

    def __init__(self, args):
        self.command_type = 'D'
        self.start = int(args)

    def start_job(self):
        _status = "The status of the simulator at time {}.\n"
        _contents = "The contents of the {}"
        _job = "Job Scheduling Queue"
        _first = "First Level Ready Queue"
        _second = "Second Level Ready Queue"
        _io = "I/O Wait Queue"
        _cpu = "The CPU is idle."
        _finished = "Finished List"
        _memory_left = "\n\nThere are {} blocks of main memory available in the system.\n"

        print("Event: {}   Time: {}".format(self.command_type, self.start))
        print(
            "\n************************************************************\n",
            _status.format(self.start),
            _contents.format(_job.upper()),
            "----------------------------------------\n",
            sep="\n")
        self.check_queue(settings.job_scheduling, _job)
        print(
            _contents.format(_first.upper()),
            "-------------------------------------------\n",
            sep="\n")
        self.check_queue(settings.ready_queue, _first)
        print(
            _contents.format(_second.upper()),
            "--------------------------------------------\n",
            sep="\n")
        self.check_queue(settings.secondary_queue, _second)
        print(
            _contents.format(_io.upper()),
            "----------------------------------\n",
            sep="\n")
        self.check_queue(settings.io_queue, _io)
        self.check_cpu()
        print(
            _contents.format(_finished.upper()),
            "---------------------------------\n",
            sep="\n")
        self.check_finished(),
        print(_memory_left.format(settings.memory_avail))

    @staticmethod
    def check_queue(queue, title):
        _empty = "The {} is empty.\n\n"

        if queue.empty():
            print(_empty.format(title))
        else:
            print(
                "Job #  Arr. Time  Mem. Req.  Run Time",
                "-----  ---------  ---------  --------\n",
                sep="\n")
            for job in queue:
                job.format_print()
            print("\n")

    @staticmethod
    def check_cpu():
        print(
            "The CPU  Start Time  CPU burst time left",
            "-------  ----------  -------------------",
            sep="\n")

        if current_job is None:
            print("\nThe CPU is idle.\n\n")
        else:
            current_job.print_on_cpu()

    @staticmethod
    def check_finished():

        if len(settings.finished) == 0:
            print("The Finished List is empty.")
        else:
            print(
                "Job #  Arr. Time  Mem. Req.  Run Time  Start Time  Com. Time",
                "-----  ---------  ---------  --------  ----------  ---------\n",
                sep="\n")
            for job in settings.finished:
                job.finished_print()


class Expiration(Command):
    parent: Add

    def __init__(self, parent):
        self.command_type = 'E'
        self.internal = True
        self.parent = parent
        self.start = parent.leave
        heapq.heappush(settings.time_queue, (self.start, self))

    def run(self):
        print("Event: {}   Time: {}".format(self.command_type, settings.time))
        # temp_time = settings.time - self.parent.queue_arrival
        self.parent.state = 3
        self.parent.time_left -= self.parent.quantum
        self.parent.time_on_cpu += self.parent.quantum
        settings.secondary_queue.put(settings.cpu.get())
        self.cpu_next()


class IO(Command):
    parent: Add

    def __init__(self, args):
        self.command_type = 'I'
        argv = args.split("   ")
        self.start = int(argv[0])
        self.run_time = argv[1]

    def start_job(self):
        global current_job
        self.parent = current_job
        current_job.leave = self.start
        current_job.io = self.run_time
        settings.cpu.get()
        settings.time_queue.remove(self.parent.trigger)
        current_job.state = 4
        current_job.trigger = Completion(current_job)
        settings.io_queue.put(self.parent)
        heapq.heapify(settings.time_queue)
        self.cpu_next()


class Termination(Command):
    parent: Add

    def __init__(self, parent):
        self.command_type = 'T'
        self.internal = True
        self.parent = parent
        self.start = parent.leave
        heapq.heappush(settings.time_queue, (self.start, self))

    def run(self):
        print("Event: {}   Time: {}".format(self.command_type, self.start))
        self.parent.leave = settings.time
        self.parent.time_left = 0
        self.parent.time_on_cpu += settings.time - self.parent.queue_arrival
        settings.memory_avail += self.parent.mem
        settings.finished.append(self.parent)
        settings.cpu.get()
        self.cpu_next()
