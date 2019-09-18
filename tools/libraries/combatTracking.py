from dndice import basic, Mode

from abilitiesLib import Abilities, AbilityName
from helpers import d20_roll
from interface import DataInterface


class Actor:
    def __init__(self, initiative=None):
        self.initiative = self.roll_initiative(initiative)

    def __lt__(self, other: 'Actor'):
        return self.initiative < other.initiative

    @staticmethod
    def roll_initiative(custom=None) -> int:
        if custom:
            return basic(custom)
        else:
            return basic(d20_roll())


class Monster(Actor):
    def __init__(self, data: dict):
        super().__init__()
        self.record = DataInterface(data)
        self.abilities = Abilities(self.record.cd('/abilities'))
        self.initiative += self.abilities.modifier(AbilityName.DEX)
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
    def __init__(self, initiative):
        super().__init__(initiative)
