from . import characterLib as char
from .exceptionsLib import OverflowSpells, OutOfSpells
from .helpers import sanitize_filename
from .interface import JsonInterface
from .settingsLib import RestLength


class SpellResource:
    def __init__(self, character: 'char.Character'):
        self.character = character
        self.record = character.record.cd('/spellcasting')

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
    def __init__(self, character):
        super().__init__(character)
        caster = JsonInterface('class/CASTER.super.class')
        cl = self.character.classes[0]
        if len(self.character.classes) == 1:
            t = cl.get('/spellcasting/slots')
            if t is None:
                self.max_spell_slots = []
            lv = self.character.classes.level
        else:
            t = 'full'
            lv = self.character.classes.caster_level
        path = '/max_spell_slots/{}/{}'.format(t, lv)
        self.max_spell_slots = caster.get(path)

    def cast(self, level: int):
        slots = self.record.get('/slots')
        if slots[level] < 1:
            # TODO: genericize LowOnResource to accommodate spells
            raise OutOfSpells(self.character, level)
        # Does this actually mutate the list? or does it mutate a copy?
        slots[level] -= 1

    def regain(self, level: int):
        slots = self.record.get('/slots')
        if slots[level] >= self.max_spell_slots[level]:
            raise OverflowSpells(self.character, level)
        slots[level] += 1

    def reset(self):
        self.record.set('/slots', self.max_spell_slots)


class SpellPoints(SpellResource):
    def __init__(self, character):
        super().__init__(character)
        caster = JsonInterface('class/CASTER.super.class')
        self.max_points = caster.get('/max_spell_points')
        self.costs = caster.get('/spell_point_cost')

    def cast(self, level: int):
        cost = self.costs[level]
        current = self.record.get('/points')
        if current < cost:
            raise OutOfSpells(self.character, level)
        self.record.set('/points', current - cost)

    def regain(self, level: int):
        points = self.costs[level]
        current = self.record.get('/points')
        if points + current > self.max_points:
            raise OverflowSpells(self.character, level)
        self.record.set('/points', points + current)

    def reset(self):
        self.record.set('/points', self.max_points)


class WarlockSlots(SpellSlots):
    def __init__(self, character):
        SpellResource.__init__(self, character)
        # Intentionally avoid SpellSlots initialization because that
        # determines caster type by the character's classes which would
        # conflict with the warlock's spell slots
        caster = JsonInterface('class/CASTER.super.class')
        self.max_slots = caster.get('/max_spell_slots/warlock')

    def rest(self, length: RestLength):
        if length >= RestLength.SHORT:
            self.reset()


class SpellsPrepared:
    def __init__(self, jf: JsonInterface, character: 'char.Character'):
        self.record = jf
        self.owner = character
        self.preparedToday = []
        self.preparedPermanently = []
        for name in jf.get('/prepared_today'):
            pass

    def prepare(self, name: str):
        self.preparedToday

    def __open_spell(self, name: str):
        filename = f"spell/{sanitize_filename(name)}.spell"
        return JsonInterface(filename, readonly=True)
