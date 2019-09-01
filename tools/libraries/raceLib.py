from interface import JSONInterface


class Race:
    def __init__(self, spec):
        file = 'race/{}.race'.format(spec['race'])
        self.interface = JSONInterface(file, readonly=True)
        self.name = spec['race']
        if 'subrace' in spec:
            file = 'race/{}.{}.sub.race'.format(spec['race'], spec['subrace'])
            sub = JSONInterface(file, readonly=True)
            self.subrace = Subrace(sub)
            self.interface += sub
            self.name = spec['subrace'] + ' ' + self.name

    def get(self, path):
        return self.interface.get(path)


class Subrace:
    def __init__(self, interface):
        self.interface = interface
