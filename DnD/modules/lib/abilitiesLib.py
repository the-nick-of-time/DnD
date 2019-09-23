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
        self.values = {name: Ability(name, inter.cd('/' + name.value))
                       for name in AbilityName}

    def __getitem__(self, ability: AbilityName) -> 'Ability':
        return self.values[ability]

    def __setitem__(self, key: AbilityName, value: int):
        if not isinstance(value, int):
            raise TypeError('Ability scores are integers')
        self.values[key].score = value

    def __iter__(self):
        yield from self.values.values()


class Ability:
    def __init__(self, name: AbilityName, inter: iface.DataInterface):
        self.name = name
        self.record = inter
        self.abbreviation = name.value[:3].upper()

    @property
    def score(self):
        return self.record.get('/')

    @score.setter
    def score(self, value: int):
        self.record.set('/', value)

    @property
    def modifier(self):
        return int((self.score - 10) // 2)
