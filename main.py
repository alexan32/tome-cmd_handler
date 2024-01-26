from lark import Lark, Token, Transformer
from lark.exceptions import UnexpectedInput
from execution import execute
import json

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


if __name__ == "__main__":

    with open("./commands4.lark") as f:
        grammar = f.read()
    
    with open("./composite.txt") as f:
        commands = [x.strip() for x in f.readlines() if len(x.strip()) != 0]

    with open("./character.json") as f:
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
            print(f"RESPONSE: {result}")

        print("=" * 30)

    print("DONE!")
    print(json.dumps(characterData, indent=4))