import re
import json
from exceptions.exceptions import *
import commands.utils as utils

def roll(tokens: list, characterData:dict):
    
    op = tokens.pop(0)

    if op == "list":
        return rollList(tokens, characterData)
    elif op == "search":
        return rollSearch(tokens, characterData)
    elif op == "delete":
        return rollDelete(tokens, characterData)
    else:
        return rollSubject(op, tokens, characterData)


def rollList(tokens:list, characterData:dict):
    index = 0
    if len(tokens) > 0 and re.fullmatch(r"\d+", tokens[0]):
        index = int(tokens[0])

    return utils.paginateDict(utils.buildCombinedRollDictionary(characterData), index)


def rollSearch(tokens:list, characterData:dict):
    if len(tokens) == 0:
        raise MissingArgumentException("Expected a search term.")

    searchResults = utils.search(tokens[0], utils.rollKeys(characterData))
    if len(searchResults) == 0:
        return f"No results found for {tokens[0]}"
    else:
        message = f"Search results for \"{tokens[0]}\":\n"
        for key in searchResults:
            message = f"{key}".ljust(utils.SPACING, ".") + f"{utils.findRoll(key, characterData)}\n"
        return message

def rollDelete(tokens:list, characterData:dict):
    if len(tokens) == 0:
        raise MissingArgumentException("Expected the name of a roll to be deleted.")
    
    key = tokens[0]
    if not key in characterData["rolls"]:
        raise NotFoundException(key, "roll")

    del characterData["rolls"][key]
    return f"successfully deleted roll \"{key}\""

def rollSubject(subject:str, tokens:list, characterData:dict):
    
    if len(tokens) == 0:
        key, total, resultString = utils.evaluateRollString(subject, characterData)
        if not key:
            return "", resultString
        return key, resultString
    
    if tokens[0] == "=" and len(tokens) == 2:
        return rollCreate(subject, tokens[1], characterData)
    
    else:
        raise InvalidArgumentException(tokens[2], "")


def rollCreate(key, value, characterData):

    if key in utils.RESERVE_WORDS:
        raise ReservewordException()
    
    if utils.rollAlreadyExists(key, characterData):
        return f"The roll name \"{key}\" is already taken."
    
    characterData["rolls"][key] = value

    return f"Created roll \"{key}\" = {value}"
