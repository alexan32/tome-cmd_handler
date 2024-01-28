import re
import json
from .exceptions import *
from . import utils


def counter(tokens: list, characterData: dict):
    op = tokens.pop(0)

    if op == "create":
        return counterCreate(tokens, characterData)
    elif op == "list":
        return counterList(tokens, characterData)
    elif op == "search":
        return counterSearch(tokens, characterData)
    elif op == "delete":
        return counterDelete(tokens, characterData)
    else:
        return counterSubject(op, tokens, characterData)

def counterCreate(tokens: list, characterData: dict):
    counterName = tokens.pop(0)

    if utils.rollAlreadyExists(counterName, characterData):
        raise AlreadyExistsException(counterName)

    newCounter = {
        "max": "10",
        "min": "0",
        "total": "10"
    }

    for token in tokens:
        if not re.fullmatch(utils.COUNTER_SET, token):
            raise InvalidArgumentException(token, "expected arguments are \"max\", \"min\", or \"total\", and must be set equal to a whole number.")
        key, value = token.split("=")
        newCounter[key] = value

    characterData["counters"][counterName] = newCounter
    utils.setUpdateFlag(characterData)
    return utils.buildCommandResponse("created counter \"counterName\": " + json.dumps(newCounter, indent=4))

def counterList(tokens: list, characterData: dict):
    index = 0
    if len(tokens) > 0 and re.fullmatch(r"\d+", tokens[0]):
        index = int(tokens[0])

    transformerFunc = lambda key, dictionary: utils.counterToString(dictionary[key])
    return utils.buildCommandResponse(utils.paginateDict(characterData["counters"], index, transformerFunction=transformerFunc))

def counterSearch(tokens: list, characterData: dict):
    if len(tokens) == 0:
        raise MissingArgumentException("Expected a search term.")
    
    searchResults = utils.search(tokens[0], list(characterData["counters"].keys()))
    if len(searchResults) == 0:
        return utils.buildCommandResponse(f"No results found for {tokens[0]}")
    else:
        message = f"Search results for \"{tokens[0]}\":\n"
        for x in searchResults:
            message += f"{x}\n"
        return utils.buildCommandResponse(message)

def counterDelete(tokens: list, characterData: dict):
    if len(tokens) == 0:
        raise MissingArgumentException("Expected the name of a counter to delete.")

    counterName = tokens[0]
    if counterName in characterData["counters"]:
        del characterData["counters"][counterName]
        utils.setUpdateFlag(characterData)
        return utils.buildCommandResponse(f"{counterName} successfully deleted.")
    else:
        raise NotFoundException(counterName, "counter")

def counterSubject(counterName: str, tokens: list, characterData: dict):
    if not counterName in characterData["counters"]:
        raise NotFoundException(counterName, "counter")
    counter = characterData["counters"][counterName]

    # no operation, just show total/max
    if len(tokens) == 0:
        return utils.buildCommandResponse(f"{counterName}: {counter['total']}/{counter['max']}" )

    # max
    elif tokens[0] == "max":
        counter["total"] = counter["max"]
        utils.setUpdateFlag(characterData)
        return utils.buildCommandResponse(f"{counterName}: {counter['total']}/{counter['max']}" )
    
    # min
    elif tokens[0] == "min":
        counter["total"] = counter["min"]
        utils.setUpdateFlag(characterData)
        return utils.buildCommandResponse(f"{counterName}: {counter['total']}/{counter['max']}")

    # increment operation
    elif re.fullmatch(utils.INCREMENT, tokens[0]):
        if len(tokens) > 1:
            raise InvalidArgumentException(tokens[1], f"Cannot have additional arguments ({tokens[1]}) after an increment argument ({tokens[0]})")

        incrementCounter(counter, tokens[0])
        utils.setUpdateFlag(characterData)
        return utils.buildCommandResponse(f"{counterName}: {counter['total']}/{counter['max']}")

    # modify operation
    elif re.fullmatch(utils.COUNTER_SET, tokens[0]):
        setValues(tokens, counter)
        characterData["counters"][counterName] = counter
        utils.setUpdateFlag(characterData)
        return utils.buildCommandResponse(f"updated counter \"{counterName}\": " + json.dumps(counter, indent=4))
    
    else:
        raise InvalidArgumentException(tokens[0], f"Expected an increment (+1, -12, etc) or a set argument (max=100).")

def setValues(tokens, counter):

    for token in tokens:
        if not re.fullmatch(utils.COUNTER_SET, token):
            raise InvalidArgumentException(token, "expected arguments are \"max\", \"min\", or \"total\", and must be set equal to a whole number.")
        key, value = token.split("=")
        counter[key] = value
        incrementCounter(counter, "+0")

def incrementCounter(counter: dict, increment: str):

    _inc = eval("0" + increment)
    _max = int(counter["max"])
    _min = int(counter["min"])
    total = int(counter["total"]) + _inc
    if total > _max:
        total = _max
    elif total < _min:
        total = _min
    counter["total"] = str(total)
