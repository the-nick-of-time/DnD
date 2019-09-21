from . import characterLib as char
from .exceptionsLib import OverflowSpells, OutOfSpells
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


class SpellsPrepared:
    def __init__(self, jf: JsonInterface, character: 'char.Character'):
        self.record = jf
        self.owner = character
        self.preparedToday = []
        self.preparedPermanently = []
        for name in jf.get('/prepared_today'):
            pass

    def prepare(self, name: str):
        self.record.set('/prepared_today/-', name)

    def __open_spell(self, name: str):
        filename = f"spell/{sanitize_filename(name)}.spell"
        return JsonInterface(filename, readonly=True)
