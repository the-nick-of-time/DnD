import enum
from typing import Union

from dndice import basic

from . import characterLib as char


class BonusType(enum.Enum):
    AC = 'AC'
    BASE_AC = 'base_AC'
    LUCK = 'lucky'
    SPELL_DC = 'spell_DC'
    ATTACK_ROLL = 'attack_roll'
    DAMAGE = 'damage'
    CANTRIP_DAMAGE = 'cantrip_damage'
    SPELL_LIST = 'spells_list'
    ALWAYS_PREPARED = 'always_prepared'
    JACK_OF_ALL_TRADES = 'jack_of_all_trades'
    CRIT_RANGE = 'crit_range'
    WEAPON_DAMAGE = 'weapon_damage'
    INITIATIVE = 'initiative'
    SPEED = 'speed'
    # Saves
    SAVE_STR = 'save_Strength'
    SAVE_DEX = 'save_Dexterity'
    SAVE_CON = 'save_Constitution'
    SAVE_INT = 'save_Intelligence'
    SAVE_WIS = 'save_Wisdom'
    SAVE_CHA = 'save_Charisma'
    # Bare checks
    CHECK_STR = 'check_Strength'
    CHECK_DEX = 'check_Dexterity'
    CHECK_CON = 'check_Constitution'
    CHECK_INT = 'check_Intelligence'
    CHECK_WIS = 'check_Wisdom'
    CHECK_CHA = 'check_Charisma'
    # Skills
    SKILL_Athletics = 'skill_Athletics'
    SKILL_Acrobatics = 'skill_Acrobatics'
    SKILL_Sleight_of_Hand = 'skill_Sleight of Hand'
    SKILL_Stealth = 'skill_Stealth'
    SKILL_Arcana = 'skill_Arcana'
    SKILL_History = 'skill_History'
    SKILL_Investigation = 'skill_Investigation'
    SKILL_Nature = 'skill_Nature'
    SKILL_Religion = 'skill_Religion'
    SKILL_Animal_Handling = 'skill_Animal Handling'
    SKILL_Insight = 'skill_Insight'
    SKILL_Medicine = 'skill_Medicine'
    SKILL_Perception = 'skill_Perception'
    SKILL_Survival = 'skill_Survival'
    SKILL_Deception = 'skill_Deception'
    SKILL_Intimidation = 'skill_Intimidation'
    SKILL_Performance = 'skill_Performance'
    SKILL_Persuasion = 'skill_Persuasion'
    # Since I don't really do turn tracking this is probably not necessary to code
    ATTACKS = 'attacks'


class Bonus:
    def __init__(self, field, value):
        self.field = field
        self.value = value


class OwnedBonus(Bonus):
    def __init__(self, field, value, character: 'char.Character'):
        super().__init__(field, value)
        self.owner = character
        self.value = basic(self.owner.parse_vars(self.value))


class OwnedBonuses:
    def __init__(self, character: 'char.Character'):
        self.owner = character

    def get(self, name: Union[BonusType, str], default=None):
        if isinstance(name, str):
            name = BonusType(name)
