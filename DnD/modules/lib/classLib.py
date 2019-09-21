import enum
from pathlib import Path
from typing import Union, Dict, List

from . import abilitiesLib as abil
from . import characterLib as char
from . import featureLib as feature
from . import helpers as h
from . import interface as iface


class CasterType(enum.Enum):
    FULL = 'full'
    HALF = 'half'
    THIRD = 'third'
    WARLOCK = 'warlock'
    NONCASTER = None


class Class:
    __slots__ = 'name', 'subclass', 'superclasses', 'level', 'interface'

    def __init__(self, spec):
        self.name = spec['class']
        self.level = spec['level']
        filename = Path('class') / h.sanitize_filename('{}.class'.format(self.name))
        base = iface.JsonInterface(filename, readonly=True)
        supers = base.get('/superclass')
        self.superclasses = []
        for name in supers:
            filename = Path('class') / h.sanitize_filename('{}.super.class'.format(name))
            file = iface.JsonInterface(filename, readonly=True)
            self.superclasses.append(Superclass(file))
        self.interface = iface.LinkedInterface(*map(lambda sc: sc.interface, self.superclasses), base)
        if 'subclass' in spec:
            filename = Path('class') / h.sanitize_filename('{}.{}.sub.class'
                                                           .format(self.name, spec['subclass']))
            file = iface.JsonInterface(filename, readonly=True)
            self.subclass = Subclass(spec['subclass'], file)
            self.interface += file

    def __str__(self):
        name = self.name
        if hasattr(self, 'subclass'):
            name += ' ({})'.format(self.subclass.name)
        return name

    def features_at_level(self, level: int) -> List[feature.Feature]:
        pass

    @property
    def HD(self) -> str:
        return self.interface.get('/hit_dice')

    @property
    def casterLevel(self) -> int:
        typ = CasterType(self.interface.get('/spellcasting/slots'))
        if typ == CasterType.FULL:
            return self.level
        if typ == CasterType.HALF:
            return self.level // 2
        if typ == CasterType.THIRD:
            return self.level // 3
        return 0

    @property
    def casterType(self) -> CasterType:
        return CasterType(self.interface.get('/spellcasting/slots'))

    @property
    def spellsAvailable(self) -> Dict[int, List[str]]:
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

    def features_at_level(self, level: int) -> List[feature.Feature]:
        pass


class Classes:
    def __init__(self, jf: iface.DataInterface):
        self.classes = [Class(spec) for spec in jf.get('/')]

    def __getitem__(self, item) -> Class:
        if isinstance(item, int):
            # Raises IndexError
            return self.classes[item]
        if isinstance(item, str):
            for cls in self.classes:
                if cls.name == item:
                    return cls
            raise KeyError('The named class was not found')
        raise KeyError('Look up a class by name or index')

    def __iter__(self):
        yield from self.classes

    def __len__(self):
        return len(self.classes)

    def __str__(self):
        return ', '.join(str(c) for c in self.classes)

    def features_at_level(self, level: int) -> List[feature.Feature]:
        pass

    @property
    def casterLevel(self) -> int:
        return sum(c.casterLevel for c in self.classes)

    @property
    def casterType(self) -> CasterType:
        casterClasses = [c for c in self.classes
                         if c.casterLevel > 0
                         and c.casterType != CasterType.WARLOCK]
        if len(casterClasses) == 0:
            return CasterType.NONCASTER
        if len(casterClasses) > 1:
            return CasterType.FULL
        # Only one caster class
        return casterClasses[0].casterType

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
    def spellsAvailable(self):
        rv = {lv: [] for lv in range(10)}
        for c in self.classes:
            for lv, spells in c.spellsAvailable.items():
                rv[lv].extend(spells)
        return rv

    @property
    def saveProficiencies(self):
        names = self.classes[0].interface.get('/proficiencies/saves')
        return [abil.AbilityName(name) for name in names]


class OwnedClasses(Classes):
    def __init__(self, jf: iface.DataInterface, character: 'char.Character'):
        super().__init__(jf)
        self.owner = character

    @property
    def proficiency(self) -> Union[int, str]:
        source = iface.JsonInterface('class/ALL.super.class')
        if self.owner.settings.proficiencyDice:
            return source.get('/proficiency/dice/' + str(self.level))
        return source.get('/proficiency/bonus/' + str(self.level))
