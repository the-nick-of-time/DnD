import enum


class Settings:
    def __init__(self, spec):
        self.healing = spec['HEALING']
        self.proficiencyDice = spec['PROFICIENCY_DICE']
        self.spellPoints = spec['SPELL_POINTS']


class HealingMode(enum.Enum):
    FAST = 'fast'
    VANILLA = 'vanilla'
    SLOW = 'slow'
