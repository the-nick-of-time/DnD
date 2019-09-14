import enum

import helpers as h
from interface import JSONInterface


class AbilityName(enum.Enum):
    STRENGTH = STR = 'Strength'
    DEXTERITY = DEX = 'Dexterity'
    CONSTITUTION = CON = 'Constitution'
    INTELLIGENCE = INT = 'Intelligence'
    WISDOM = WIS = 'Wisdom'
    CHARISMA = CHA = 'Charisma'


class Abilities:
    def __init__(self, jf: JSONInterface):
        self.record = jf
        self.values = {name: Ability(name, jf.get('/' + name)) for name in AbilityName}

    def __getitem__(self, ability: AbilityName):
        return self.values[ability].score

    def __setitem__(self, key: AbilityName, value: int):
        if not isinstance(value, int):
            raise TypeError('Ability scores are integers')
        self.values[key] = value

    def modifier(self, ability: AbilityName):
        return self.values[ability].modifier


class Ability:
    def __init__(self, name: AbilityName, score: int):
        self.name = name
        self.score = score
        self.abbreviation = name[:3].upper()

    @property
    def modifier(self):
        return h.modifier(self.score)
