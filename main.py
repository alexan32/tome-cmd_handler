import json
from lark import Lark, Token, Transformer
from lark.exceptions import UnexpectedInput

from commands.counter import counter
from commands.composite import composite
from commands.roll import roll
from exceptions.exceptions import InvalidCommandException

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

COMMAND_FUNCTIONS = {
    "counter": counter,
    "composite": composite,
    "roll": roll,
    "article": None,  # TODO: Add article cmd
    "func": None,  # TODO: Add func cmd
    "function": None  # TODO: Add function cmd
}

def execute(tokens: list, characterData: dict):
    
    command = tokens.pop(0)
    cmd_function = COMMAND_FUNCTIONS.get(command)

    if cmd_function:
        return cmd_function(tokens, characterData)
    else:
        raise InvalidCommandException(command)


if __name__ == "__main__":

    with open("./commands.lark") as f:
        grammar = f.read()
    
    with open("./input.txt") as f:
        commands = [x.strip() for x in f.readlines() if len(x.strip()) != 0]

    with open("./character-min.json") as f:
        characterData = json.load(f)

    parser = CommandParser(grammar, "command_phrase")

    for command in commands:
        print(f"INPUT: {command}")
        try:
            tree, tokens = parser.parse(command)
        except Exception as e:
            print("Failed to parse input. Use !help for a list of valid commands.")
        else:
            print(f"TOKENS: {tokens}")
            # print(tree.pretty())
            result = execute(tokens, characterData)
            print(f"RESPONSE:\n{result}")

        print("=" * 30)

    print("DONE!")
    print(json.dumps(characterData, indent=4))