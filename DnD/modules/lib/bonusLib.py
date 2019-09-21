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
    # Since I don't really do turn tracking this is probably not necessary to code
    ATTACKS = 'attacks'
    WEAPON_DAMAGE = 'weapon_damage'
    INITIATIVE = 'initiative'
    SPEED = 'speed'


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
