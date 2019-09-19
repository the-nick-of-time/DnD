import enum

from .interface import JsonInterface


class Settings:
    def __init__(self, jf: JsonInterface):
        self.record = jf
        self.healing = property(
            lambda: self.record.get('/HEALING') or HealingMode.VANILLA,
            lambda value: self.record.set('/HEALING', value),
            lambda: self.record.delete('/HEALING')
        )
        self.spellPoints = property(
            lambda: self.record.get('/SPELL_POINTS') or False,
            lambda value: self.record.set('/SPELL_POINTS', value),
            lambda: self.record.delete('/SPELL_POINTS')
        )
        self.proficiencyDice = property(
            lambda: self.record.get('/PROFICIENCY_DICE') or False,
            lambda value: self.record.set('/PROFICIENCY_DICE', value),
            lambda: self.record.delete('/PROFICIENCY_DICE')
        )

    def serialize(self):
        rv = {}
        if self.healing != HealingMode.VANILLA:
            rv['HEALING'] = self.healing
        if self.spellPoints:
            rv['SPELL_POINTS'] = True
        if self.proficiencyDice:
            rv['PROFICIENCY_DICE'] = True
        return rv


class HealingMode(enum.Enum):
    FAST = 'fast'
    VANILLA = 'vanilla'
    SLOW = 'slow'


class RestLengths(enum.Enum):
    LONG = 100
    SHORT = 10
    TURN = 1
    NOTHING = 0

    @classmethod
    def from_string(cls, value):
        if value == 'long' or value == 'long rest':
            return RestLengths.LONG
        elif value == 'short' or value == 'short rest':
            return RestLengths.SHORT
        elif value == 'turn':
            return RestLengths.TURN
        else:
            return RestLengths.NOTHING
