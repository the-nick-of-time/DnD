from interface import JSONInterface


class Item:
    def __init__(self, name: str, spec: dict):
        types = spec['type'].split()
        fmt = '{}/{}.{}'
        filename = fmt.format(types[-1], name, '.'.join(types))
        self.record = JSONInterface(filename, readonly=True)
        self.name = self.record.get('/name')
        self.value = self.record.get('/value')
        self.weight = self.record.get('/weight')
        self.consumes = self.record.get('/consumes')
        self.effect = self.record.get('/effect')
        self.description = self.record.get('/description')

    def use(self) -> str:
        # TODO: consume item
        return self.effect

    def describe(self) -> str:
        return self.description
