from typing import List, Union

from dndice import basic, verbose

from . import characterLib as char
from . import helpers as h
from . import interface as iface


class Attack:
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        self.record = jf
        self.owner = character
        self.actions = [OneAttack(jf.cd('/actions/' + str(i)), self.owner)
                        for i, att in enumerate(self.record.get('/actions'))]


class OneAttack:
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        self.record = jf
        self.owner = character
        self.onHit = Effect(self.record.cd('/on_hit'), character)
        self.onMiss = Effect(self.record.cd('/on_miss'), character)
        typ = self.record.get("/to_hit/type")
        if typ == 'SPELLSAVE':
            self.toHit = SpellSave(self.record.cd('to_hit'), self.owner)
        elif typ == 'ATTACKROLL':
            self.toHit = AttackRoll(self.record.cd('/to_hit'), self.owner)
        elif typ == 'AUTOHIT':
            self.toHit = AutoHit(self.record.cd('/to_hit'), self.owner)
        else:
            self.toHit = CustomToHit(self.record.cd('/to_hit'), self.owner)


class ToHit:
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        self.record = jf
        self.character = character
        self.modifiers = Modifiers(jf.get('/modifiers'), character)

    def value(self, advantage=False, disadvantage=False) -> str:
        """Tells the user what they got on their to-hit."""
        raise NotImplementedError


class AttackRoll(ToHit):
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        super().__init__(jf, character)
        self.against = 'AC'

    def value(self, advantage=False, disadvantage=False) -> str:
        roll = h.d20_roll(advantage, disadvantage, self.character.bonuses.get('lucky', False))
        proficiency = self.character.proficiency

        mod = self.modifiers.get_value()
        return verbose(roll, modifiers=mod)


class SavingThrow(ToHit):
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        super().__init__(jf, character)
        self.against = jf.get('/against')


class SpellSave(SavingThrow):
    pass


class AutoHit(ToHit):
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        super().__init__(jf, character)

    def value(self, advantage=False, disadvantage=False) -> str:
        return 'This attack automatically hits.'


class CustomToHit(ToHit):
    pass


class Effect:
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        self.record = jf
        self.character = character
        self.damage = Damage(jf.cd('/damage'), character)


class Damage:
    def __init__(self, jf: iface.DataInterface, character: char.Character):
        self.record = jf
        self.character = character
        self.baseRoll = jf.get('/base_roll')
        self.damageType = jf.get('/damage_type')
        self.rollSuffix = jf.get('/roll_suffix')
        self.modifiers = Modifiers(jf.get('/modifiers'), character)


class Modifiers:
    def __init__(self, mods: List[Union[str, int, List[str, int]]], character: char.Character):
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
                    mod = self.character.parse_vars(mod)
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
                            mod = self.character.parse_vars(mod)
                        candidate = basic(candidate)
                    # Take largest seen so far
                    if largest is None:
                        largest = candidate
                    elif candidate > largest:
                        largest = candidate
                value += largest
        return value
