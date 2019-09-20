import enum

from .exceptionsLib import OutOfItems
from .interface import JsonInterface
from .itemLib import Item


class Inventory:
    def __init__(self, jf: JsonInterface):
        self.record = jf
        self.entries = {name: ItemEntry(name, jf.cd('/' + name)) for name in jf.get('/')}

    def __getitem__(self, item):
        return self.entries[item]

    def consume_item(self, name):
        if name not in self.entries:
            raise OutOfItems(name)
        item = self.entries[name]
        if item.quantity < 1:
            raise OutOfItems(name)
        item.quantity -= 1


class EquipmentSlot(enum.Enum):
    OFF_HAND = 'off_hand'
    MAIN_HAND = 'main_hand'
    BELT = 'belt'
    CLOTHES = 'clothes'
    PANTS = 'pants'
    HEAD = 'head'
    CLOAK = 'cloak'
    NECK = 'neck'
    LEFT_FOOT = 'left_foot'
    RIGHT_FOOT = 'right_foot'


class EquipmentType(enum.Enum):
    GLOVES = 'gloves'
    BELT = 'belt'
    LIGHT_ARMOR = 'light_armor'
    MEDIUM_ARMOR = 'medium_armor'
    HEAVY_ARMOR = 'heavy_armor'
    CLOTHES = 'clothes'
    HEADWEAR = 'headwear'
    BOOTS = 'boots'
    NECKLACE = 'necklace'
    CLOAK = 'cloak'
    SHIELD = 'shield'
    WEAPON_1H = 'one_hand_weapon'
    WEAPON_2H = 'two_hand_weapon'

    __slotMap = {
        GLOVES: [EquipmentSlot.OFF_HAND, EquipmentSlot.MAIN_HAND],
        BELT: [EquipmentSlot.BELT],
        LIGHT_ARMOR: [EquipmentSlot.CLOTHES, EquipmentSlot.PANTS],
        MEDIUM_ARMOR: [EquipmentSlot.CLOTHES, EquipmentSlot.PANTS],
        HEAVY_ARMOR: [EquipmentSlot.CLOTHES, EquipmentSlot.PANTS],
        CLOTHES: [EquipmentSlot.CLOTHES, EquipmentSlot.PANTS],
        HEADWEAR: [EquipmentSlot.HEAD],
        BOOTS: [EquipmentSlot.LEFT_FOOT, EquipmentSlot.RIGHT_FOOT],
        NECKLACE: [EquipmentSlot.NECK],
        CLOAK: [EquipmentSlot.CLOAK],
        SHIELD: [EquipmentSlot.OFF_HAND],
        WEAPON_1H: [EquipmentSlot.MAIN_HAND],
        WEAPON_2H: [EquipmentSlot.OFF_HAND],
    }

    def slots(self):
        return self.__slotMap[self]


class ItemEntry:
    def __init__(self, name: str, jf: JsonInterface):
        self.record = jf
        self.item = Item(name, jf.get('/'))

    @property
    def quantity(self) -> int:
        return self.record.get('/number')

    @quantity.setter
    def quantity(self, value):
        self.record.set('/quantity', value)

    @property
    def equipped(self) -> EquipmentType:
        return self.record.get('/equipped')

    @equipped.setter
    def equipped(self, value: EquipmentType):
        self.record.set('/equipped', value)
