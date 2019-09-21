from . import characterLib as char
from . import inventoryLib as inv
from . import itemLib as item


class Apparel(item.Item):
    def __init__(self, name: str, spec: dict):
        super().__init__(name, spec)
        self.base_AC = self.record.get('/base_AC')
        # equip_slot is how we know it's equippable
        self.equip_slot = inv.EquipmentType(self.record.get('/type'))


class OwnedApparel(Apparel):
    def __init__(self, name: str, spec: dict, character: 'char.Character'):
        super().__init__(name, spec)
        self.owner = character
