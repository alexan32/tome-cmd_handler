from main import execute
import json

with open("./character2.json") as f:
    character = json.load(f)

with open("./character-min.json") as f:
    characterMin = json.load(f)


messages = execute("composite create temp max=100 total=32", characterMin)
print(messages)