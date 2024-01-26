import json
from lark import Lark, Token, Transformer
from lark.exceptions import UnexpectedInput

from commands.counter import counter
from commands.composite import composite
from commands.roll import roll
from commands.function import function
from exceptions.exceptions import InvalidCommandException, RecursiveDepthExceeded

class TokenSimplifier(Transformer):

    def set_argument(self, tree):
        newValue = tree[0].value + tree[1].value + tree[2].value
        return Token("set_argument", newValue)

class CommandParser:

    def __init__(self, grammar:str, startingRule:str):
        self.grammar = grammar
        self.parser = Lark(self.grammar, start=startingRule)
        self.tokenSimplifier = TokenSimplifier()

    def parse(self, _input:str):

        try:
            tree = self.tokenSimplifier.transform(self.parser.parse(_input))
            tokens = [x.value for x in tree.scan_values(lambda v: isinstance(v, Token))]
        except UnexpectedInput as e:
            print(e)
            raise e

        return tree, tokens

with open("./commands.lark") as f:
    grammar = f.read()

PARSER = CommandParser(grammar, "command_phrase")

COMMAND_FUNCTIONS = {
    "counter": counter,
    "composite": composite,
    "roll": roll,
    # "article": None,  # TODO: Add article cmd
    "func": function,
    "function": function
}

MAXIMUM_DEPTH = 5

def execute(commandPhrase:str, characterData: dict, depth:int=0):
    
    messages = []

    _, tokens = PARSER.parse(commandPhrase)
    command = tokens.pop(0)
    cmd_function = COMMAND_FUNCTIONS.get(command)

    if cmd_function:
        output = cmd_function(tokens, characterData)
        # print(f"MESSAGE: \n{output[0]}")
        messages.append(output[0])
        
        # function commands may return a list of other commands to execute
        for _commandPhrase in output[1]:

            # check for maximum depth
            if depth > MAXIMUM_DEPTH:
                raise RecursiveDepthExceeded(MAXIMUM_DEPTH)

            # collect message results from execution
            newMessages = execute(_commandPhrase, characterData, depth+1)
            messages.extend(newMessages)
        return messages
    else:
        raise InvalidCommandException(command)


if __name__ == "__main__":

    with open("./input.txt") as f:
        commands = [x.strip() for x in f.readlines() if len(x.strip()) != 0]

    with open("./character2.json") as f:
        characterData = json.load(f)

    for command in commands:
        print(f"INPUT: {command}")
        results = execute(command, characterData)
        print(f"OUTPUT:")
        for x in results:
            print(x)
        print("=" * 30)

    print("DONE!")
    # print(json.dumps(characterData, indent=4))