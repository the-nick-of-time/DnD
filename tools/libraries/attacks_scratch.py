from typing import Union, List

from dndice import basic

import classes as c
import helpers as h
import interface


# class SingleAttack:
#     def __init__(self, jf: interface.JsonInterface, index: int):
#         self.jf = jf
#         self.path = '/attacks/' + str(index)
#         self.character = None
#
#     def to_hit(self, advantage: bool, disadvantage: bool, rollSuffixes: list, modifiers: list):
#         mods = modifiers + (self.jf.get(self.path + '/to_hit/modifiers') or [])
#         suffixes = rollSuffixes + (self.jf.get(self.path + '/to_hit/roll_suffix') or [])
#
#     def attack_roll(self, advantage: bool, disadvantage: bool, suffixes: list, modifiers: list):
#         baseDice = h.d20_roll(advantage, disadvantage,
#                               self.character.bonuses.get('lucky', False) if self.character is not None else False)
#         baseRoll = r.roll(baseDice + ''.join(suffixes))
#         # TODO: modifiers list follows same conventions as damage: if item is value, take it; if item is collection, take highest from collection
#         bonus = sum(self.character.parse_vars(modifiers) if self.character is not None else modifiers)
#         return baseRoll + bonus
#
#     def spell_save(self, spell: c.Spell):
#         return self.character.save_DC(spell) if self.character else None
#
#     def custom(self, suffixes: list, modifiers: list):
#         baseDice = self.jf.get(self.path)
#         baseRoll = r.roll(baseDice + ''.join(suffixes))
#         bonus = sum(self.character.parse_vars(modifiers) if self.character is not None else modifiers)
#         return baseRoll + bonus
#
#     def set_owner(self, character: c.Character):
#         self.character = character
#
#     def parse_modifiers(self):


class ToHit:
    def __init__(self, jf: interface.JsonInterface, path: str, character: c.Character):
        self.jf = jf
        self.path = path
        self.character = character
        self.modifiers = Modifiers(jf.get('/modifiers'), self.character)


class AttackRoll(ToHit):
    def __init__(self, jf: interface.JsonInterface, path: str, character: c.Character):
        super().__init__(jf, path, character)

    def rollToHit(self, adv=False, dis=False, luck=False):
        rollstr = h.d20_string(adv, dis, luck) + ''.join(self.jf.get(self.path + '/roll_suffix'))
        mod = self.modifiers.get_value()
        return basic(rollstr, modifiers=mod)


class SpellSave(ToHit):
    def __init__(self, jf: interface.JsonInterface, path: str, character: c.Character):
        super().__init__(jf, path, character)
        self.target = jf.get(self.path + '/against')

    def get_dc(self):
        return self.character.save_DC()


class Modifiers:
    def __init__(self, mods: List[Union[str, int, List[str, int]]], character: c.Character):
        self.character = character
        self.mods = mods

    def get_value(self) -> Union[int, float]:
        value = 0
        for mod in self.mods:
            if isinstance(mod, int):
                value += mod
            elif isinstance(mod, str):
                if '$' in mod:
                    # this contains character variables
                    mod = self.character.parse_vars(mod, False)
                value += basic(mod)
            elif isinstance(mod, list):
                if len(mod) == 0:
                    # Add zero to the value
                    continue
                largest = None
                for candidate in mod:
                    if isinstance(candidate, str):
                        if '$' in mod:
                            # this contains character variables
                            mod = self.character.parse_vars(mod, False)
                        candidate = basic(candidate)
                    # Take largest seen so far
                    if largest is None:
                        largest = candidate
                    elif candidate > largest:
                        largest = candidate
                value += largest
        return value
