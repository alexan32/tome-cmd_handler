import re
import json
from exceptions.exceptions import *
import commands.utils as utils

def roll(tokens: list, characterData:dict):
    
    op = tokens.pop(0)

    if op == "list":
        pass
    elif op == "search":
        pass
    elif op == "delete":
        pass
    else:
        pass


def rollList(tokens:list, characterData:dict):
    pass

def rollSearch(tokens:list, characterData:dict):
    pass

def rollDelete(tokens:list, characterData:dict):
    pass

def rollSubject(subject:str, tokens:list, characterData:dict):
    pass