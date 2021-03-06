from .helpers import sanitize_filename
from .interface import JsonInterface


class Item:
    def __init__(self, name: str, spec: dict):
        types = spec['type'].split()
        fmt = '{}/{}.{}'
        filename = fmt.format(types[-1], sanitize_filename(name), '.'.join(types))
        self.record = JsonInterface(filename, readonly=True)
        self.name = self.record.get('/name')
        self.value = self.record.get('/value')
        self.weight = self.record.get('/weight')
        self.consumes = self.record.get('/consumes')
        self.effect: str = self.record.get('/effect')
        self.description: str = self.record.get('/description')

    def use(self) -> str:
        # TODO: consume item
        return self.effect

    def describe(self) -> str:
        return self.description
