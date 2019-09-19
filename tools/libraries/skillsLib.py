from dndice import basic

import abilitiesLib as abil
from helpers import d20_roll


class Skill:
    def __init__(self, name: str, ability: abil.Ability):
        self.name = name
        self.ability = ability

    def roll(self, advantage=False, disadvantage=False, lucky=False):
        d20 = d20_roll(advantage, disadvantage, lucky)
        return basic(d20, modifiers=self.ability.modifier)


class Skills:
    pass
