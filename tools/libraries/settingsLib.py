import enum


class Settings:
    def __init__(self):
        raise NotImplementedError

    @classmethod
    def initialize(cls, spec):
        cls.healing = spec.get('HEALING', HealingMode.VANILLA)
        cls.proficiencyDice = spec.get('PROFICIENCY_DICE', False)
        cls.spellPoints = spec.get('SPELL_POINTS', False)

    @classmethod
    def serialize(cls):
        rv = {}
        try:
            if cls.healing != HealingMode.VANILLA:
                rv['HEALING'] = cls.healing
            if cls.proficiencyDice:
                rv['PROFICIENCY_DICE'] = True
            if cls.spellPoints:
                rv['SPELL_POINTS'] = True
            return rv
        except AttributeError:
            return {}


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
        if value == 'long':
            return RestLengths.LONG
        elif value == 'short':
            return RestLengths.SHORT
        elif value == 'turn':
            return RestLengths.TURN
        else:
            return RestLengths.NOTHING
