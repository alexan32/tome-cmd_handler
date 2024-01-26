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

    return utils.buildCommandResponse(f"Created function \"{funcName}\"")

def functionList(tokens:list, characterData:dict):
    pass

def functionSearch(tokens:list, characterData:dict):
    pass

def functionDelete(tokens:list, characterData:dict):
    pass

def functionSubject(funcName:str, tokens:list, characterData:dict):
    
    if not funcName in characterData["functions"]:
        raise NotFoundException(funcName, "function")
    
    # split saved function into args and commands
    funcString = characterData["functions"][funcName]
    argString, commandString = funcString.split("|")
    args = [x for x in argString.split(" ") if len(x) != 0]

    # match current input with expected args
    argsDict = {}
    for arg in args:
        nextToken = tokens.pop(0)
        if nextToken == "|":
            raise MissingArgumentException(f"function \"{funcName}\" expects the following args: {args}")
        argsDict[arg] = nextToken

    # perform string replacement on commandstring
    for key in argsDict:
        commandString = commandString.replace(key, argsDict[key])

    nextCommands = [x.strip() for x in commandString.split(";") if len(x) != 0]
    # print(f"NEXT COMMANDS: {nextCommands}")
    return utils.buildCommandResponse(f"executing function \"{funcName}\".", nextCommands)

    
