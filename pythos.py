import commands
import settings
from os_queues import OSQueue

# PythOS Global Variables
memory = 512


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


if __name__ == '__main__':

    settings.init()

    while True:
        try:
            cmd = cmd_create(input())
            cmd.run()

        except EOFError:
            break
