from dndice import basic, Mode

from . import abilitiesLib as abil
from . import helpers as h
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
        self.initiative += self.abilities.modifier(abil.AbilityName.DEX)
        mode = Mode.from_string('average' if data.get('average') else 'normal')
        self.HP = basic(data['HP'], mode=mode)
        self.maxHP = self.HP
        self.AC = data['AC']

    def alter_HP(self, amount):
        self.HP += basic(amount)
        if self.HP < 0:
            self.HP = 0
        elif self.HP > self.maxHP:
            self.HP = self.maxHP


class CharacterStub(Actor):
    def __init__(self, name, initiative):
        super().__init__(name, initiative)
