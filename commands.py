import settings


class Command:
    start = leave = mem = job_id = run_time = io = time_left = quantum = queue_arrival = 0
    internal = False
    command_type: chr

    def start(self):
        print("Event: {}   Time: {}".format(self.command_type, self.start))


class Add(Command):

    def __init__(self, args):
        self.command_type = 'A'

        argv = args.split("   ")
        self.start = int(argv[0])
        self.job_id = int(argv[1])
        self.mem = int(argv[2])
        self.run_time = self.time_left = int(argv[3])

    def start(self):

        if self.mem > settings.memory:
            print("This job exceeds the system's main memory capacity.")
            return

        print("Event: {}   Time: {}".format(self.command_type, self.start))
        settings.job_scheduling.put(self)

    def format_print(self):
        print("%5d\t\t%4d\t\t%3d\t\t%5d\n" % (self.job_id, self.start, self.mem, self.run_time))


class CurJob(Add):
    def print_on_cpu(self):
        print("%7d\t\t%7d\t\t\t%12d" % (self.job_id, self.start, self.time_left))


current_job: CurJob = None


class Completion(Command):

    def __init__(self, args):
        self.command_type = 'C'
        self.internal = True


class Display(Command):

    def __init__(self, args):
        self.command_type = 'D'

        self.start = int(args)
        self.job_id = current_job

    def start(self):

        _status = "The status of the simulator at time {}.\n"
        _contents = "The contents of the {}\n"
        _job = "Job Scheduling Queue"
        _first = "First Level Ready Queue"
        _second = "Second Level Ready Queue"
        _io = "I/O Wait Queue"
        _cpu = "The CPU is idle."
        _finished = "Finished List"
        _memory_left = "There are {} blocks of main memory available in the system.\n"

        print(
            "************************************************************\n",
            "\n",
            _status.format(self.start),
            "\n",
            _contents.format(_job.upper()),
            "----------------------------------------\n",
            "\n",
            self.check_queue(settings.job_scheduling, _job),
            "\n",
            _contents.format(_first.upper()),
            "-------------------------------------------\n",
            "\n",
            self.check_queue(settings.ready_queue, _first),
            "\n",
            _contents.format(_second.upper()),
            "--------------------------------------------\n"
            "\n",
            self.check_queue(settings.io_queue, _io),
            "\n",
            self.check_cpu(),
            "\n",
            _contents.format(_finished.upper()),
            "--------------------------------------------\n",
            "\n",
            self.check_finished(),
            "\n",
            _memory_left.format(settings.memory),
            "\n"
              )

    @staticmethod
    def check_queue(queue, title):

        _empty = "The {} is empty.\n"

        if queue.empty():
            print(_empty.format(title))
        else:
            print(
                "Job #  Arr. Time  Mem. Req.  Run Time  Start Time  Com. Time",
                "-----  ---------  ---------  --------  ----------  ---------",
                "\n"
                  )
            for job in queue:
                job.format_print()

    @staticmethod
    def check_cpu():

        print(
            "The CPU  Start Time  CPU burst time left",
            "-------  ----------  -------------------",
            "\n"
              )

        if current_job is None:
            print("The CPU is idle")
        else:
            current_job.print_on_cpu()

    @staticmethod
    def check_finished():

        if settings.finished.empty():
            print("The Finished List is empty.")
        else:
            print(
                "Job #  Arr. Time  Mem. Req.  Run Time\n",
                "-----  ---------  ---------  --------\n",
            )
            for job in settings.finished:
                job.finished_print()


class Expiration(Command):

    def __init__(self, args):
        self.command_type = 'E'
        self.internal = True


class IO(Command):

    def __init__(self, args):
        self.command_type = 'I'

        argv = args.split("   ")
        self.start = argv[0]
        self.run_time = argv[1]

    def start(self):
        current_job.leave = self.start
        current_job.io = self.run_time


class Termination(Command):

    def __init__(self, args):
        self.command_type = 'T'
        self.internal = True
