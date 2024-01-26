from difflib import SequenceMatcher
from d20 import roll
import re

# Regex
COMPOSITE_SET = r"[a-z_]+\=[\$a-z0-9\+\-\(\),\/%*_]+"
COUNTER_SET = r'(max|min|total)\=\d+'
INCREMENT = r'[+-]\d+'
DICE_OPERATORS = r"(k|p|rr|ro|ra|e|mi|ma)(l|h)?"
VARIABLE = r"([a-ce-z][a-z_]*|d[a-z_]+)"

# Constants for pagination and formatting
CHARACTERS_PER_PAGE = 800
ROWS_PER_PAGE = 20
HEADER_LENGTH = 30
SPACING = 25

# Reserve words
OPERATION_WORDS = [
    "create",
    "search",
    "list",
    "delete",
    "remove",
]
COMMAND_WORDS = [
    "counter", 
    "composite", 
    "roll", 
    "article", 
    "func",
    "function"
]
RESERVE_WORDS =  [*OPERATION_WORDS, *COMMAND_WORDS]

# Other
MAX_DEPTH = 10


def rollKeys(characterData:dict):
    return [
        *list(characterData["rolls"].keys()),
        *list(characterData["counters"].keys()),
        *list(characterData["composites"].keys())
    ]

def rollAlreadyExists(key: str, characterData:dict):
    return key in rollKeys(characterData)

def findRoll(key:str, characterData:dict):
    if key in characterData["rolls"]:
        return characterData["rolls"][key]
    elif key in characterData["composites"]:
        return compositeToString(characterData["composites"][key])
    elif key in characterData["counters"]:
        return characterData["counters"][key]["total"]
    return None


def compositeToString(composite: dict) -> str:
    keys = composite.keys()
    values = map(lambda key : composite[key], keys)
    rollString = " + ".join(values).lower()
    return rollString

def counterToString(counter:dict) -> str:
    return f"{counter['total']} / {counter['max']}"


def buildCombinedRollDictionary(characterData:dict, compositeMarker="`"):
    data = {}
    for key in characterData["composites"]:
        data[key] = compositeMarker + compositeToString(characterData["composites"][key])
    for key in characterData["counters"]:
        data[key] = counterToString(characterData["counters"][key])
    return {
        **data,
        **characterData["rolls"]
    }


def search(searchTerm: str, searchData: list, maxResults=10):
    accepted = {}
    for value in searchData:
        ratio = SequenceMatcher(None, searchTerm, value).ratio()
        if ratio > 0.6:
            accepted[value] = ratio
            if len(accepted.keys()) >= maxResults:
                for key in accepted.keys():
                    if ratio > accepted[key]:
                        del accepted[key]
                        accepted[value] = ratio
                        break
            else:
                accepted[value] = ratio

    return list(accepted.keys())


def basicTransform(key: str, dictionary: dict):
    return dictionary[key]

def paginateDict(dictionary: dict, index: int, transformerFunction=basicTransform, spacing:int=SPACING, spaceCharacter:str=".", minspace:int=0):
    keys = sorted(list(dictionary.keys()))
    pages = []
    message = ""
    counter = 0

    for key in keys:
        # Create a line with key and transformed value
        line = f"{key}{spaceCharacter*minspace}".ljust(spacing, spaceCharacter) + f"{transformerFunction(key, dictionary)}\n"
        counter += 1

        # Check if adding the line exceeds the page limits
        if len(line) + len(message) >= CHARACTERS_PER_PAGE or counter >= ROWS_PER_PAGE:
            pages.append(message)
            message = ""
            counter = 0

        message += line

    # Add any remaining message to the pages
    if message != "":
        pages.append(message)

    # Ensure the index is within bounds
    index -= 1
    if index < 0:
        index = 0
    if index > len(pages) - 1:
        index = 0

    # Create a header and return the current page
    header = f"Page {index+1}/{len(pages)}" + " ".ljust(HEADER_LENGTH, "=")
    return header + "\n" + pages[index]


def paginateList(data: list, index: int):
    pages = []
    message = ""
    counter = 0

    for key in data:
        # Create a line for each item in the list
        line = f"{key}\n"
        counter += 0

        # Check if adding the line exceeds the page limits
        if len(line) + len(message) >= CHARACTERS_PER_PAGE or counter >= ROWS_PER_PAGE:
            pages.append(message)
            message = ""
            counter = 0

        message += line

    # Add any remaining message to the pages
    if message != "":
        pages.append(message)

    # Create a header and return the current page
    header = f"Page {index+1}/{len(pages)}" + " ".ljust(HEADER_LENGTH, "=")
    return header + "\n" + pages[index]


# returns a set containing the following:
# key - either string or None. returns the string if the input matches a saved value in the characterData data, otherwise None
# total - string representing the total of the dice roll
# roll - the string representing the final dice expression including the total
def evaluateRollString(rollString:str, characterData:dict, depth:int=0, logging=False) -> set:
    rollString = rollString.strip()
    key = None
    _print = lambda content : print("".ljust(depth, "\t") + content) if logging else None

    # if rollstring is a variable, we want to set it to its saved value for display purposes.
    if depth == 0 and re.fullmatch(r"\b" + VARIABLE + r"\b", rollString):
        _print(f"depth level 0 '{rollString}' is a variable!")
        key = rollString
        rollString = findRoll(rollString, characterData)
        _print(f"found match for {rollString}: '{rollString}'")
        if not rollString:
            raise Exception(f'No data found for "{rollString}"')

    # find all variables, and make sure to ignore operations like "kh1", "kl2", etc
    matches = re.findall(VARIABLE, rollString)
    matches = [x for x in matches if not re.fullmatch(DICE_OPERATORS, x)]
    _print(f"rollString: '{rollString}'. matches: {matches}")

    # perform string replacements
    misses = []
    for match in matches:
        replaceValue = findRoll(match, characterData)
        _print(f"FIND ROLL FOR {match} ==> {replaceValue}")
        if replaceValue:
            if not replaceValue.isdigit():
                if depth == MAX_DEPTH:
                    raise Exception(f"'evaluateRollString' function maximum depth ({MAX_DEPTH}) reached! Failed to replace '{replaceValue}'.")
                _print(f"RECURSIVE CALL! '{match}' ==> '{replaceValue}'?")
                _, replaceValue, _ = evaluateRollString(replaceValue, characterData, depth=depth+1, logging=logging)
                _print(f"DONE! '{match}' ==> '{replaceValue}'")
            exact = r"\b(" + match + r")\b" # make sure you are not matching on a portion of another var. ie 'dex' in 'dexterity'
            _print(f"performing replacement on {exact}")
            rollString = re.sub(exact, replaceValue, rollString)
        else:
            _print(f"no variable for {match}")
            misses.append(match)
    
    if len(misses) > 0:
        raise Exception(f"Failed to perform variable replacement for the following: {misses}")
    
    # roll result, return values
    result = roll(rollString)
    return key, str(result.total), str(result)

def buildCommandResponse(message:str, nextCommands:list=[]):
    return message, nextCommands