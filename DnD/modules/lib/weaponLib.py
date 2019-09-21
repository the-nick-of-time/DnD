from . import inventoryLib as inv
from . import itemLib as item


class Weapon(item.Item):
    def __init__(self, name: str, spec: dict):
        super().__init__(name, spec)
        hands = self.record.get('/hands')
        # equip_slot is how we know it's equippable
        if hands == 'one':
            self.equip_slot = inv.EquipmentType.WEAPON_1H
        elif hands == 'two':
            self.equip_slot = inv.EquipmentType.WEAPON_2H
        else:
            self.equip_slot = None
