import re
import json
from exceptions.exceptions import *
import commands.utils as utils


def function(tokens: list, characterData: dict):
    op = tokens.pop(0)

    if op == "create":
        return functionCreate(tokens, characterData)
    elif op == "list":
        return functionList(tokens, characterData)
    elif op == "search":
        return functionSearch(tokens, characterData)
    elif op == "delete":
        return functionDelete(tokens, characterData)
    else:
        return functionSubject(op, tokens, characterData)
    

def functionCreate(tokens:list, characterData:dict):
    funcName = tokens.pop(0)

    if funcName in characterData["functions"]:
        raise AlreadyExistsException()
    
    args = []
    while tokens[0][0] == "$":
        args.append(tokens.pop(0))

    separator = tokens.pop(0)

    statements = ""
    while len(tokens) > 0:
        token = tokens.pop(0)
        if token != ";":
            statements += " " + token
        else:
            statements += "; "
    
    saveString = (" ".join(args) + " | " + statements).strip()

    characterData["functions"][funcName] = saveString

    return f"Created function \"{funcName}\""

def functionList(tokens:list, characterData:dict):
    pass

def functionSearch(tokens:list, characterData:dict):
    pass

def functionDelete(tokens:list, characterData:dict):
    pass

def functionSubject(tokens:list, characterData:dict):
    pass