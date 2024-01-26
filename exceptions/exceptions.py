commands = ["counter", "composite", "roll", "article", "func"]

class CommandHandlerException(Exception):
    """Parent exception for custom command handler exceptions."""
    pass

class InvalidCommandException(CommandHandlerException):
    def __init__(self, badCommand):
        super().__init__(f"Received an invalid command \"{badCommand}\". Expected one of {commands}")

class InvalidArgumentException(CommandHandlerException):
    def __init__(self, badArg, expected):
        super().__init__(f"Received an invalid argument \"{badArg}\". {expected}")

class AlreadyExistsException(CommandHandlerException):
    def __init__(self, key, type):
        super().__init__(f"A {type} with a key of {key} already exists.")

class NotFoundException(CommandHandlerException):
    def __init__(self, key, type):
        super().__init__(f"{type} {key} was not found in character data.")

class MissingArgumentException(CommandHandlerException):
    def __init__(self, expected):
        super().__init__(f"Command was missing an expected argument. {expected}")