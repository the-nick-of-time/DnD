import enum
from typing import Union, Dict, List

import characterLib as char
from interface import JsonInterface, LinkedInterface


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
        base = JsonInterface('class/{}.class'.format(self.name), readonly=True)
        supers = base.get('/superclass')
        self.superclasses = []
        for name in supers:
            filename = 'class/{}.super.class'.format(name)
            file = JsonInterface(filename, readonly=True)
            self.superclasses.append(Superclass(file))
        self.interface = LinkedInterface(*map(lambda sc: sc.interface, self.superclasses), base)
        if 'subclass' in spec:
            filename = 'class/{}.{}.sub.class'.format(self.name, spec['subclass'])
            file = JsonInterface(filename, readonly=True)
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

    @property
    def spells_available(self) -> Dict[int, List[str]]:
        # TODO: Update /spellcasting/known for every spellcasting class
        #  with their spell lists in the format level: ["spells"]
        return self.interface.get('/spellcasting/known')


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
    def __init__(self, jf: JsonInterface, character: 'char.Character'):
        self.classes = [Class(spec) for spec in jf.get('/')]
        self.owner = character

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.classes[item]
        if isinstance(item, str):
            for cls in self.classes:
                if cls.name == item:
                    return cls
            raise KeyError('The named class was not found')

    def __iter__(self):
        yield from self.classes

    @property
    def features(self):
        pass

    @property
    def proficiency(self) -> Union[int, str]:
        source = JsonInterface('class/ALL.super.class')
        if self.owner.settings.proficiencyDice:
            return source.get('/proficiency/1/' + str(self.level))
        return source.get('/proficiency/0/' + str(self.level))

    @property
    def casterLevel(self) -> int:
        return sum(c.casterLevel for c in self.classes)

    @property
    def level(self) -> int:
        return sum(c.level for c in self.classes)

    @property
    def maxHD(self) -> Dict[str, int]:
        rv = {}
        for c in self.classes:
            hd = c.HD
            if hd in rv:
                rv[hd] += c.level
            else:
                rv[hd] = c.level
        return rv

    @property
    def spells_available(self):
        rv = {lv: [] for lv in range(10)}
        for c in self.classes:
            for lv, spells in c.spells_available.items():
                rv[lv].extend(spells)
        return rv
