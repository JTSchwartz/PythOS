import settings
import heapq
import re

current_job = None


class Command:
    start = leave = mem = job_id = run_time = io = state = time_left = quantum = queue_arrival = time_on_cpu = hit = 0
    internal = been_to_cpu = False
    command_type = None

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
    trigger = None

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
        global current_job

        if self.state == 1:
            if not self.been_to_cpu:
                self.been_to_cpu = True
                self.hit = settings.time

            settings.cpu_from_second = False

            self.quantum = 100
        else:
            settings.cpu_from_second = True

            self.quantum = 300

        self.queue_arrival = settings.time
        current_job = self

        if self.time_left <= self.quantum:
            self.state = 6
            self.leave = settings.time + self.time_left
            self.trigger = Termination(self)
        else:
            self.state = 2
            self.leave = settings.time + self.quantum
            self.trigger = Expiration(self)

    def format_print(self):
        print("%5d%11d%11d%10d" % (self.job_id, self.start, self.mem, self.run_time))

    def print_on_cpu(self):
        print("\n%7d%12d%21d\n\n" % (self.job_id, self.hit, self.time_left - (settings.time - self.queue_arrival)))

    def io_print(self):
        print("%5d%11d%11d%10d%15d%10d%12d" % (self.job_id, self.start, self.mem, self.run_time, (self.leave - self.io), self.io, self.leave))

    def finished_print(self):
        print("%5d%11d%11d%10d%12d%11d" % (self.job_id, self.start, self.mem, self.run_time, self.hit, self.leave))


class Completion(Command):
    parent = None

    def __init__(self, arg):
        self.command_type = 'C'
        self.internal = True
        self.parent = arg
        heapq.heappush(settings.time_queue, (self.parent.leave, self))

    def run(self):
        global current_job

        print("Event: {}   Time: {}".format(self.command_type, settings.time))
        settings.io_queue.remove(self.parent)
        self.parent.state = 1
        settings.ready_queue.put(self.parent)

        if settings.cpu_from_second and not settings.cpu.empty():
            replace = settings.cpu.get()
            time_on = settings.time - replace.queue_arrival
            replace.quantum -= time_on
            replace.time_left -= time_on
            replace.state = 3
            settings.secondary_queue.put(replace)

            for signal in settings.time_queue:
                if signal[1].parent.job_id == replace.job_id:
                    settings.time_queue.remove(signal)
                    break

            current_job = settings.ready_queue.get()
            settings.cpu.put(current_job)
            current_job.run()

        if settings.cpu.empty():
            self.cpu_next()


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
        self.check_io()
        self.check_cpu()
        print(
            _contents.format(_finished.upper()),
            "---------------------------------\n",
            sep="\n")
        self.check_finished(),
        print(_memory_left.format(settings.memory_avail))

    @staticmethod
    def check_io():
        if len(settings.io_queue) == 0:
            print("The I/O Wait Queue is empty.\n\n")
        else:
            print(
                "Job #  Arr. Time  Mem. Req.  Run Time  IO Start Time  IO Burst  Comp. Time",
                "-----  ---------  ---------  --------  -------------  --------  ----------\n",
                sep="\n")
            temp_list = []
            for job in settings.io_queue:
                heapq.heappush(temp_list, (job.io, job))

            for x in range(len(temp_list)):
                heapq.heappop(temp_list)[1].io_print()

            print("\n")

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
    parent = None

    def __init__(self, parent):
        self.command_type = 'E'
        self.internal = True
        self.parent = parent
        self.start = parent.leave
        heapq.heappush(settings.time_queue, (self.start, self))

    def run(self):
        print("Event: {}   Time: {}".format(self.command_type, settings.time))
        self.parent.state = 3
        self.parent.time_left -= self.parent.quantum
        self.parent.time_on_cpu += self.parent.quantum
        settings.secondary_queue.put(settings.cpu.get())
        self.cpu_next()


class IO(Command):
    parent = None

    def __init__(self, args):
        self.command_type = 'I'
        argv = re.split("\s+", args)
        self.start = int(argv[0])
        self.run_time = int(argv[1])

    def start_job(self):
        print("Event: {}   Time: {}".format(self.command_type, self.start))
        if settings.cpu.empty():
            self.cpu_next()
            return
        self.parent = settings.cpu.get()
        self.parent.time_left -= settings.time - self.parent.queue_arrival
        self.parent.leave = settings.time + self.run_time
        self.parent.io = self.run_time
        for job in settings.time_queue:
            if job[1].parent.job_id == self.parent.job_id:
                settings.time_queue.remove(job)
                break
        self.parent.state = 4
        self.parent.trigger = Completion(self.parent)
        settings.io_queue.append(self.parent)
        self.cpu_next()


class Termination(Command):
    parent = None

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
