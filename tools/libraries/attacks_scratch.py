import interface
import classes as c
import rolling as r
import helpers as h


class SingleAttack:
    def __init__(self, jf: interface.JSONInterface, index: int):
        self.jf = jf
        self.path = '/attacks/' + str(index)
        self.character = None

    def to_hit(self, advantage: bool, disadvantage: bool, rollSuffixes: list, modifiers: list):
        mods = modifiers + (self.jf.get(self.path + '/to_hit/modifiers') or [])
        suffixes = rollSuffixes + (self.jf.get(self.path + '/to_hit/roll_suffix') or [])

    def attack_roll(self, advantage: bool, disadvantage: bool, suffixes: list, modifiers: list):
        baseDice = h.d20_roll(advantage, disadvantage,
                              self.character.bonuses.get('lucky', False) if self.character is not None else False)
        baseRoll = r.roll(baseDice + ''.join(suffixes))
        # TODO: modifiers list follows same conventions as damage: if item is value, take it; if item is collection, take highest from collection
        bonus = sum(self.character.parse_vars(modifiers) if self.character is not None else modifiers)
        return baseRoll + bonus

    def spell_save(self, spell: c.Spell):
        return self.character.save_DC(spell) if self.character else None

    def custom(self, suffixes: list, modifiers: list):
        baseDice = self.jf.get(self.path)
        baseRoll = r.roll(baseDice + ''.join(suffixes))
        bonus = sum(self.character.parse_vars(modifiers) if self.character is not None else modifiers)
        return baseRoll + bonus

    def set_owner(self, character: c.Character):
        self.character = character
