from dndice import basic, Mode

from . import abilitiesLib as abil
from . import helpers as h
from . import hpLib as hp
from . import interface as iface


class Actor:
    def __init__(self, name: str, initiative=None):
        self.name = name
        self.initiative = self.roll_initiative(initiative)

    def __lt__(self, other: 'Actor'):
        return self.initiative < other.initiative

    @staticmethod
    def roll_initiative(custom=None) -> int:
        if custom:
            return basic(custom)
        else:
            return basic(h.d20_roll())


class Monster(Actor):
    __slots__ = 'name', 'HP', 'AC', 'abilities'

    def __init__(self, data: dict):
        super().__init__(data['name'])
        self.record = iface.DataInterface(data)
        self.abilities = abil.Abilities(self.record.cd('/abilities'))
        self.initiative += self.abilities[abil.AbilityName.DEX].modifier
        self.hpRoll = data['HP']
        mode = Mode.from_string('average' if data.get('average') else 'normal')
        maxHP = int(basic(self.hpRoll, mode=mode))
        self.HP = hp.HP(iface.DataInterface({
            "current": maxHP,
            "max": maxHP,
            "temp": 0,
        }))
        self.AC = data['AC']


class CharacterStub(Actor):
    def __init__(self, name, initiative):
        super().__init__(name, initiative)
