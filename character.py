class Counter:

    def __init__(self, counterData:dict) -> None:
        self.max = counterData["max"]
        self.min = counterData["min"]
        self.total = counterData["total"]

    def operate(*args, **kwargs):
        pass

class Character:

    def __init__(self, characterData:dict) -> None:
        self.meta = characterData["meta"]
        self.routines = characterData["routines"]
        self.articles = characterData["articles"]
        self.counters = characterData["counters"]
        self.variables = characterData["variables"]
        self.formulas = characterData["formulas"]
        self.composites = characterData["composites"]

    def findRoll(self, key:str):
        if key in self.variables:
            return self.variables[key]
        elif key in self.formulas:
            return self.formulas[key]
        elif key in self.composites:
            return self.compositeToString(self.composites[key])
        elif key in self.counters:
            return self.counters[key]["total"]
        return None

    # converts a dictionary that represents a roll into a roll string
    def compositeToString(self, rollDict: dict) -> str:
        keys = rollDict.keys()
        values = map(lambda key : rollDict[key], keys)
        values = [x for x in values if x not in ["", "0", 0, None]]
        rollString = " + ".join(values).lower()
        return rollString
    
    def save():
        print("TODO! implement save")
        return 200