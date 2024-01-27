from . import utils

class CommandHandlerException(Exception):
    """Parent exception for custom command handler exceptions."""
    pass

class InvalidCommandException(CommandHandlerException):
    def __init__(self, badCommand):
        super().__init__(f"Received an invalid command \"{badCommand}\". Expected one of {utils.COMMAND_WORDS}")

class InvalidArgumentException(CommandHandlerException):
    def __init__(self, badArg, expected):
        super().__init__(f"Received an invalid argument \"{badArg}\". {expected}")

class AlreadyExistsException(CommandHandlerException):
    def __init__(self, key):
        super().__init__(f"A value of this type with name \"{key}\" already exists.")

class NotFoundException(CommandHandlerException):
    def __init__(self, key, type):
        super().__init__(f"{type} {key} was not found in character data.")

class MissingArgumentException(CommandHandlerException):
    def __init__(self, expected):
        super().__init__(f"Command was missing an expected argument. {expected}")

class ReservewordException(CommandHandlerException):
    def __init__(self):
        super().__init__(f"The following are reserve words and cannot be used to name resources: {utils.RESERVE_WORDS}")

class RecursiveDepthExceeded(CommandHandlerException):
    def __init__(self, depth) -> None:
        super().__init__(f"A recursive function hit the maximum depth permitted: {depth}")