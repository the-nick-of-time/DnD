import enum

from dndice import verbose, compile

from . import characterLib as char
from . import helpers as h
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
        return self.values[ability].score

    def __setitem__(self, key: AbilityName, value: int):
        if not isinstance(value, int):
            raise TypeError('Ability scores are integers')
        self.values[key].score = value

    def modifier(self, ability: AbilityName):
        return self.values[ability].modifier


class Ability:
    def __init__(self, name: AbilityName, score: int):
        self.name = name
        self.score = score
        self.abbreviation = name[:3].upper()

    @property
    def modifier(self):
        return int((self.score - 10) // 2)

    def save(self, advantage=False, disadvantage=False, luck=False):
        roll = h.d20_roll(advantage, disadvantage, luck)
        return verbose(roll, modifiers=self.modifier)


class OwnedAbility(Ability):
    def __init__(self, name: AbilityName, score: int, character: 'char.Character'):
        super().__init__(name, score)
        self.owner = character

    def save(self, advantage=False, disadvantage=False, luck=False):
        roll = h.d20_roll(advantage, disadvantage, self.owner.bonuses.get('luck'))
        roll += compile(self.owner.bonuses.get(self.name + '_save', 0))
        roll += compile(self.modifier)
        return verbose(roll)
