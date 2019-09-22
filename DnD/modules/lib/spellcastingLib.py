from pathlib import Path

from . import characterLib as char
from . import spellLib as sp
from .exceptionsLib import OverflowSpells, OutOfSpells, AlreadyPrepared
from .helpers import sanitize_filename
from .interface import DataInterface, JsonInterface
from .settingsLib import RestLength


class SpellResource:
    def __init__(self, jf: DataInterface):
        self.record = jf

    def cast(self, level: int):
        raise NotImplementedError

    def regain(self, level: int):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def rest(self, length: RestLength):
        if length >= RestLength.LONG:
            self.reset()


class SpellSlots(SpellResource):
    def __init__(self, jf: DataInterface):
        super().__init__(jf)
        # ABSTRACT
        self.max_spell_slots = None

    def cast(self, level: int):
        if level == 0:
            # Cantrips don't consume any resources
            return
        slots = self.record.get('/slots')
        if slots[level] < 1:
            raise OutOfSpells(level)
        # Does this actually mutate the list? or does it mutate a copy?
        slots[level] -= 1

    def regain(self, level: int):
        slots = self.record.get('/slots')
        if slots[level] >= self.max_spell_slots[level]:
            raise OverflowSpells(level)
        slots[level] += 1

    def reset(self):
        self.record.set('/slots', self.max_spell_slots)


class OwnedSpellSlots(SpellSlots):
    def __init__(self, jf: DataInterface, character: 'char.Character'):
        super().__init__(jf)
        self.owner = character
        caster = JsonInterface('class/CASTER.super.class')
        path = '/max_spell_slots/{}/{}'.format(self.owner.classes.casterType.value,
                                               self.owner.classes.casterLevel)
        self.max_spell_slots = caster.get(path)


class SpellPoints(SpellResource):
    def __init__(self, jf: DataInterface):
        super().__init__(jf)
        self.max_points = None
        self.costs = None

    def cast(self, level: int):
        if level == 0:
            # Cantrips cost no resources
            return
        cost = self.costs[level]
        current = self.record.get('/points')
        if current < cost:
            raise OutOfSpells(level)
        self.record.set('/points', current - cost)

    def regain(self, level: int):
        points = self.costs[level]
        current = self.record.get('/points')
        if points + current > self.max_points:
            raise OverflowSpells(level)
        self.record.set('/points', points + current)

    def reset(self):
        self.record.set('/points', self.max_points)


class OwnedSpellPoints(SpellPoints):
    def __init__(self, jf: DataInterface, character: 'char.Character'):
        super().__init__(jf)
        self.owner = character
        caster = JsonInterface('class/CASTER.super.class')
        path = '/max_spell_points/{}'.format(self.owner.classes.casterLevel)
        self.max_points = caster.get(path)
        self.costs = caster.get('/spell_point_cost')


class WarlockSlots(SpellSlots):
    def __init__(self, jf: DataInterface):
        super().__init__(jf)
        self.max_spell_slots = None

    def rest(self, length: RestLength):
        if length >= RestLength.SHORT:
            self.reset()


class OwnedWarlockSlots(WarlockSlots):
    def __init__(self, jf: DataInterface, character: 'char.Character'):
        super().__init__(jf)
        self.owner = character
        caster = JsonInterface('class/CASTER.super.class')
        path = '/max_spell_slots/warlock/{}'.format(self.owner.classes['Warlock'].level)
        self.max_spell_slots = caster.get(path)


class OwnedSpellsPrepared:
    def __init__(self, jf: JsonInterface, character: 'char.Character'):
        self.record = jf
        self.owner = character
        self.prepared = []
        for name in self.preparedNames:
            self.prepare(name)

    def __getitem__(self, item):
        if isinstance(item, str):
            for spell in self.prepared:
                if spell.name == item:
                    return spell
            raise KeyError('The named spell is not prepared')
        if isinstance(item, sp.Spell):
            for spell in self.prepared:
                if spell == item:
                    return spell
            raise KeyError('The given spell is not prepared')

    @property
    def preparedNames(self):
        return (set(self.record.get('/prepared_today'))
                | set(self.record.get('/always_prepared'))
                | set(self.owner.bonuses.get('always_prepared')))

    def prepare_new(self, name: str):
        self.record.set('/prepared_today/-', name)
        self.prepare(name)

    def prepare(self, name: str):
        if name in self.preparedNames:
            raise AlreadyPrepared('{} is already prepared'.format(name))
        filename = Path('spell') / (sanitize_filename(name) + '.spell')
        record = JsonInterface(filename, readonly=True)
        spell = sp.OwnedSpell(record, self.owner)
        self.prepared.append(spell)
