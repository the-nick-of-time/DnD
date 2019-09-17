from exceptionsLib import OutOfItems
from interface import JSONInterface
from itemLib import Item


class Inventory:
    def __init__(self, jf: JSONInterface):
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


class ItemEntry:
    def __init__(self, name: str, jf: JSONInterface):
        self.record = jf
        self.item = Item(name, jf.get('/'))

    @property
    def quantity(self) -> int:
        return self.record.get('/number')

    @quantity.setter
    def quantity(self, value):
        self.record.set('/quantity', value)

    @property
    def equipped(self) -> str:
        return self.record.get('/equipped')

    @equipped.setter
    def equipped(self, value):
        self.record.set('/equipped', value)
