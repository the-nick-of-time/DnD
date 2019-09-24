import enum

from .interface import JsonInterface


class Settings:
    def __init__(self, jf: JsonInterface):
        self.record = jf

    @property
    def healing(self) -> 'HealingMode':
        return self.record.get('/HEALING') or HealingMode.VANILLA

    @healing.setter
    def healing(self, value: 'HealingMode'):
        self.record.set('/HEALING', value)

    @property
    def spellPoints(self) -> bool:
        return self.record.get('/SPELL_POINTS') or False

    @spellPoints.setter
    def spellPoints(self, value: bool):
        self.record.set('/SPELL_POINTS', value)

    @property
    def proficiencyDice(self) -> bool:
        return self.record.get('/PROFICIENCY_DICE') or False

    @proficiencyDice.setter
    def proficiencyDice(self, value: bool):
        self.record.set('/PROFICIENCY_DICE', value)

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


class RestLength(enum.IntEnum):
    LONG = 100
    SHORT = 10
    TURN = 1
    NOTHING = 0

    @classmethod
    def from_string(cls, value):
        if value == 'long' or value == 'long rest':
            return RestLength.LONG
        elif value == 'short' or value == 'short rest':
            return RestLength.SHORT
        elif value == 'turn':
            return RestLength.TURN
        else:
            return RestLength.NOTHING
