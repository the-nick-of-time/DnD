from dndice import basic

from abilitiesLib import Abilities, AbilityName
from helpers import d20_roll


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
    def __init__(self, name: str, abilities: Abilities, AC: int, ):
        super().__init__()
        self.abilities = abilities
        self.initiative += self.abilities.modifier(AbilityName.DEX)


class CharacterStub(Actor):
    def __init__(self, initiative):
        super().__init__(initiative)
