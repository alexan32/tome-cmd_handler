import re
from . exceptions import *
from . import utils


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
    
    saveString = (" ".join(args) + " |" + statements).strip()

    characterData["functions"][funcName] = saveString
    utils.setUpdateFlag(characterData)
    return utils.buildCommandResponse(f"Created function \"{funcName}\"")

def functionList(tokens:list, characterData:dict):
    index = 0
    if len(tokens) > 0 and re.fullmatch(r"\d+", tokens[0]):
        index = int(tokens[0])

    return utils.buildCommandResponse(utils.paginateDict(characterData["functions"], index, spacing=0, minspace=1, spaceCharacter=" "))


def functionSearch(tokens:list, characterData:dict):
    if len(tokens) == 0:
        raise MissingArgumentException("Expected a search term.")
    
    searchResults = utils.search(tokens[0], list(characterData["functions"].keys()))
    if len(searchResults) == 0:
        return utils.buildCommandResponse(f"No results found for {tokens[0]}")
    else:
        message = f"Search results for \"{tokens[0]}\":\n"
        for x in searchResults:
            message += f"{x}\n"
        return utils.buildCommandResponse(message)

def functionDelete(tokens:list, characterData:dict):
    if len(tokens) == 0:
        raise MissingArgumentException("Expected the name of a function to delete.")

    functionName = tokens[0]
    if functionName in characterData["functions"]:
        del characterData["functions"][functionName]
        utils.setUpdateFlag(characterData)
        return utils.buildCommandResponse(f"{functionName} successfully deleted.")
    else:
        raise NotFoundException(functionName, "functions")

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
        if len(tokens) == 0:
            raise MissingArgumentException(f"function \"{funcName}\" expects the following args: {args}")
        nextToken = tokens.pop(0)
        argsDict[arg] = nextToken

    # perform string replacement on commandstring
    for key in argsDict:
        commandString = commandString.replace(key, argsDict[key])

    nextCommands = [x.strip() for x in commandString.split(";") if len(x) != 0]
    # print(f"NEXT COMMANDS: {nextCommands}")
    return utils.buildCommandResponse(f"executing function \"{funcName}\".", nextCommands)

    
