import settings
import heapq


class Command:
    start = leave = mem = job_id = run_time = io = state = time_left = quantum = queue_arrival = time_on_cpu = 0
    internal = False
    command_type: chr


class Add(Command):

    def __init__(self, args):
        self.command_type = 'A'
        argv = args.split("   ")
        self.start = int(argv[0])
        self.job_id = int(argv[1])
        self.mem = int(argv[2])
        self.run_time = self.time_left = int(argv[3])

    def start_job(self):

        if self.mem > settings.memory:
            print("This job exceeds the system's main memory capacity.")
            return

        print("Event: {}   Time: {}".format(self.command_type, self.start))
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
            move_to_cpu(this, 100)

        def cpu_secondary(this):
            return None

        def secondary_cpu(this):
            move_to_cpu(this, 300)

        def cpu_io(this):
            return None

        def io_ready(this):
            return None

        def terminate(this):
            return None

        def move_to_cpu(this, n):
            global current_job

            this.quantum = n
            this.queue_arrival = settings.time
            current_job = this

            if self.time_left <= n:
                Termination(this)
            else:
                Expiration(this)

        _switcher = {
            1: ready_cpu,
            2: cpu_secondary,
            3: secondary_cpu,
            4: cpu_io,
            5: io_ready,
            6: terminate,
        }

        _switcher[self.state](self)

    def format_print(self):
        print("%5d\t\t%4d\t\t%3d\t\t%5d\n" % (self.job_id, self.start, self.mem, self.run_time))

    def print_on_cpu(self):
        print("%7d\t\t%7d\t\t\t%12d" % (self.job_id, self.start, self.time_left))


current_job: Add = None


class Completion(Command):

    def __init__(self, args):
        self.command_type = 'C'
        self.internal = True


class Display(Command):

    def __init__(self, args):
        self.command_type = 'D'
        self.start = int(args)

    def start_job(self):
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

    parent: Add

    def __init__(self, parent):
        self.command_type = 'E'
        self.internal = True
        self.parent = parent

    def run(self):
        print("Event: {}   Time: {}".format(self.command_type, settings.time))
        settings.secondary_queue.put(settings.cpu.get())
        global current_job

        if not settings.ready_queue.empty():
            current_job = settings.ready_queue[0].get()
            settings.cpu.put(current_job)
            current_job.run()
        else:
            current_job = settings.secondary_queue[0].get()
            settings.cpu.put(current_job)
            current_job.run()


class IO(Command):

    def __init__(self, args):
        self.command_type = 'I'
        argv = args.split("   ")
        self.start = argv[0]
        self.run_time = argv[1]

    def start_job(self):
        current_job.leave = self.start
        current_job.io = self.run_time


class Termination(Command):
    parent: Add

    def __init__(self, parent):
        self.command_type = 'T'
        self.internal = True
        self.parent = parent
        self.start = parent.time_left + settings.time
        heapq.heappush(settings.time_queue, (self.start, self))

    def run(self):
        global current_job

        print("Event: {}   Time: {}".format(self.command_type, self.start))
        settings.memory_avail += self.parent.mem
        settings.finished.append(self.parent)
        settings.cpu.get()

        if not settings.ready_queue.empty():
            current_job = settings.ready_queue[0].get()
            settings.cpu.put(current_job)
            current_job.run()
        else:
            current_job = settings.secondary_queue[0].get()
            settings.cpu.put(current_job)
            current_job.run()
