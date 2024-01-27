import json
from cmd_handler import *

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
print(json.dumps(characterData, indent=4))