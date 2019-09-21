import enum
from typing import Optional

from . import abilitiesLib as abil
from . import characterLib as char
from . import exceptionsLib as ex
from .exceptionsLib import OutOfItems
from .interface import JsonInterface
from .itemLib import Item


class Inventory:
    def __init__(self, jf: JsonInterface):
        self.record = jf
        self.entries = {name: ItemEntry(name, jf.cd('/' + name), self)
                        for name in jf.get('/')}

    def __getitem__(self, item: str) -> 'ItemEntry':
        return self.entries[item]

    def __iter__(self):
        yield from self.entries.values()

    def add(self, name: str, quantity=1, type='item', equipped=None):
        path = '/' + name
        self.record.set(path, {})
        self.record.set(path + '/type', type)
        self.record.set(path + '/quantity', quantity)
        self.record.set(path + '/equipped', equipped)
        self.entries[name] = ItemEntry(name, self.record.cd(path), self)

    def consume_item(self, name):
        if name not in self.entries:
            raise OutOfItems(name)
        item = self.entries[name]
        if item.quantity < 1:
            raise OutOfItems(name)
        item.quantity -= 1

    @property
    def totalWeight(self):
        return sum(item.weight for item in self.entries.values())

    def cleanup(self):
        for name, item in self.entries.items():
            if item.quantity < 1:
                self.record.delete('/' + name)


class OwnedInventory(Inventory):
    def __init__(self, jf: JsonInterface, character: 'char.Character'):
        super().__init__(jf)
        self.owner = character

    @property
    def encumbrance(self):
        strength = self.owner.abilities[abil.AbilityName.STRENGTH].score
        stages = ["No penalty.",
                  "Your speed drops by 10 feet.",
                  "Your speed drops by 20 feet and you have disadvantage on "
                  "all physical rolls.",
                  "You cannot carry this much weight, only push or drag it.",
                  "You cannot move this much weight."]
        thresholds = [strength * 5,
                      strength * 10,
                      strength * 15,
                      strength * 30,
                      99999]
        weight = self.totalWeight
        for s, t in zip(stages, thresholds):
            if weight <= t:
                return s

    def equip(self, item: str):
        entry = self[item]
        try:
            slots = set(entry.equip_slot.slots())
        except AttributeError:
            # not equippable
            return
        if self.owner.openEquipSlots >= slots:
            self.owner.openEquipSlots.difference_update(slots)
            entry.equipped = entry.equip_slot
        else:
            raise ex.EquipSlotsFull("Your equipment slots are full")


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
    __slots__ = ('record', 'item', 'inventory', 'name', 'value', 'weight',
                 'consumes', 'effect', 'description')

    def __init__(self, name: str, jf: JsonInterface, parent: Inventory):
        self.record = jf
        self.item = Item(name, jf.get('/'))
        self.inventory = parent

    def __getattr__(self, key):
        # Properties that aren't found should delegate to the Item
        return getattr(self.item, key)

    @property
    def quantity(self) -> int:
        return self.record.get('/number')

    @quantity.setter
    def quantity(self, value):
        self.record.set('/quantity', value)

    @property
    def equipped(self) -> Optional[EquipmentType]:
        return EquipmentType(self.record.get('/equipped'))

    @equipped.setter
    def equipped(self, value: Optional[EquipmentType]):
        # get tricksy with short-circuiting filtering the None case
        self.record.set('/equipped', value and value.value)

    def use(self):
        self.inventory.consume_item(self.item.consumes)
        return self.item.effect
