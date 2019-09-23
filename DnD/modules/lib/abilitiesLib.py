import enum

from . import interface as iface


class AbilityName(enum.Enum):
    STRENGTH = STR = 'Strength'
    DEXTERITY = DEX = 'Dexterity'
    CONSTITUTION = CON = 'Constitution'
    INTELLIGENCE = INT = 'Intelligence'
    WISDOM = WIS = 'Wisdom'
    CHARISMA = CHA = 'Charisma'


class Abilities:
    def __init__(self, inter: iface.DataInterface):
        self.record = inter
        self.values = {name: Ability(name, inter.get('/' + name.value))
                       for name in AbilityName}

    def __getitem__(self, ability: AbilityName) -> 'Ability':
        return self.values[ability]

    def __setitem__(self, key: AbilityName, value: int):
        if not isinstance(value, int):
            raise TypeError('Ability scores are integers')
        self.values[key].score = value


class Ability:
    def __init__(self, name: AbilityName, score: int):
        self.name = name
        self.score = score
        self.abbreviation = name.value[:3].upper()

    @property
    def modifier(self):
        return int((self.score - 10) // 2)
