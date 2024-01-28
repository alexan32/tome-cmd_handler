import re
import json
from . exceptions import *
from . import utils

def composite(tokens: list, characterData: dict):
    op = tokens.pop(0)

    if op == "create":
        return compositeCreate(tokens, characterData)
    elif op == "list":
        return compositeList(tokens, characterData)
    elif op == "search":
        return compositeSearch(tokens, characterData)
    elif op == "delete":
        return compositeDelete(tokens, characterData)
    else:
        return compositeSubject(op, tokens, characterData)

def compositeCreate(tokens: list, characterData: dict):
    compositeName = tokens.pop(0)

    if utils.rollAlreadyExists(compositeName, characterData):
        raise AlreadyExistsException(compositeName)

    if len(tokens) == 0:
        raise MissingArgumentException("Expected something like \"base=1d20\", \"proficiency=expert\", or \"bonus=2\"")

    newComposite = {}
    setValues(tokens, newComposite)

    characterData["composites"][compositeName] = newComposite
    utils.setUpdateFlag(characterData)
    return utils.buildCommandResponse(f"created {compositeName}: " + json.dumps(newComposite, indent=4))

def compositeTransformer(key:str, composites:dict):
    target = composites[key]
    return utils.compositeToString(target)

def compositeList(tokens: list, characterData: dict):
    index = 0
    if len(tokens) > 0 and re.fullmatch(r"\d+", tokens[0]):
        index = int(tokens[0])

    return utils.buildCommandResponse(
        utils.paginateDict(characterData["composites"], index, transformerFunction=compositeTransformer)
    )


def compositeSearch(tokens: list, characterData: dict):
    if len(tokens) == 0:
        raise MissingArgumentException("Expected a search term.")

    searchResults = utils.search(tokens[0], list(characterData["composites"].keys()))
    if len(searchResults) == 0:
        return utils.buildCommandResponse(f"No results found for {tokens[0]}")
    else:
        message = f"Search results for \"{tokens[0]}\":\n"
        for x in searchResults:
            message += f"{x}\n"
        return utils.buildCommandResponse(message)

def compositeDelete(tokens: list, characterData: dict):
    if len(tokens) == 0:
        raise MissingArgumentException("Expected the name of a composite to delete.")

    compositeName = tokens[0]
    if compositeName in characterData["composites"]:
        del characterData["composites"][compositeName]
        utils.setUpdateFlag(characterData)
        return utils.buildCommandResponse(f"composite \"{compositeName}\" successfully deleted.")
    else:
        raise NotFoundException(compositeName, "composite")

def compositeSubject(compositeName: str, tokens: list, characterData: dict):
    if not compositeName in characterData["composites"]:
        raise NotFoundException(compositeName, "composite")
    composite = characterData["composites"][compositeName]

    # no operation, just display composite
    if len(tokens) == 0:
        return utils.buildCommandResponse(f"composite \"{compositeName}\": " + json.dumps(composite, indent=4)) 
    
    # remove operation
    elif tokens[0] == "remove":
        utils.setUpdateFlag(characterData)
        return compositeRemove(compositeName, composite, tokens[1:])

    # modify operation
    elif re.fullmatch(utils.COMPOSITE_SET, tokens[0]):
        setValues(tokens, composite)
        characterData["composites"][compositeName] = composite
        utils.setUpdateFlag(characterData)
        return utils.buildCommandResponse(f"updated \"{compositeName}\": " + json.dumps(composite, indent=4))
    else:
        raise InvalidArgumentException(tokens[0], f"Expected an increment (+1, -12, etc) or a set argument (max=100). Received {tokens[0]}")

def compositeRemove(compositeName: str, composite: dict, tokens: list):
    key = tokens[0]
    if key in composite:
        del composite[key]
    else:
        raise NotFoundException(key, "composite")
    
    return utils.buildCommandResponse(f"removed \"{key}\" from \"{compositeName}\": " + json.dumps(composite, indent=4))

def setValues(tokens: list, composite: dict):
    for token in tokens:
        if not re.fullmatch(utils.COMPOSITE_SET, token):
            raise InvalidArgumentException(token, "Expected something like \"base=1d20\", \"proficiency=expert\", or \"bonus=2\"")
        key, value = token.split("=")
        composite[key] = value

# updateMessage = lambda compositeName, _composite : f"updated \"{compositeName}\": " + json.dumps(_composite, indent=4)
# removeKeyMessage = lambda compositeName, _composite, key : f"removed \"{key}\" from \"{compositeName}\": " + json.dumps(_composite, indent=4)