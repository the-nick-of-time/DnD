import enum

from interface import JSONInterface, LinkedInterface


class CasterType(enum.Enum):
    FULL = 'full'
    HALF = 'half'
    THIRD = 'third'
    WARLOCK = 'warlock'


class Class:
    __slots__ = 'name', 'subclass', 'superclasses', 'level', 'interface'

    def __init__(self, spec):
        self.name = spec['class']
        self.level = spec['level']
        base = JSONInterface('class/{}.class'.format(self.name), readonly=True)
        supers = base.get('/superclass')
        self.superclasses = []
        for name in supers:
            filename = 'class/{}.super.class'.format(name)
            file = JSONInterface(filename, readonly=True)
            self.superclasses.append(Superclass(file))
        self.interface = LinkedInterface(*map(lambda sc: sc.interface, self.superclasses), base)
        if 'subclass' in spec:
            filename = 'class/{}.{}.sub.class'.format(self.name, spec['subclass'])
            file = JSONInterface(filename, readonly=True)
            self.subclass = Subclass(spec['subclass'], file)
            self.interface += file

    @property
    def features(self):
        pass

    @property
    def HD(self):
        return self.interface.get('/hit_dice')

    @property
    def casterLevel(self):
        typ = self.interface.get('/spellcasting/slots')
        if typ == 'full':
            return self.level
        if typ == 'half':
            return self.level // 2
        if typ == 'third':
            return self.level // 3
        if typ == 'warlock':
            return self.level


class Superclass:
    __slots__ = 'interface'

    def __init__(self, interface):
        self.interface = interface


class Subclass:
    __slots__ = 'name', 'interface'

    def __init__(self, name, interface):
        self.name = name
        self.interface = interface

    @property
    def features(self):
        pass


class Classes:
    def __init__(self, specs, settings):
        self.classes = [Class(spec) for spec in specs]
        self.settings = settings

    @property
    def features(self):
        pass

    @property
    def proficiency(self):
        pass

    @property
    def casterLevel(self):
        return sum(c.casterLevel for c in self.classes)

    @property
    def level(self):
        return sum(c.level for c in self.classes)

    @property
    def maxHD(self):
        rv = {}
        for c in self.classes:
            hd = c.HD
            if hd in rv:
                rv[hd] += c.level
            else:
                rv[hd] = c.level
        return rv
