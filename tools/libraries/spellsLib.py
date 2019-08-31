import classes as c
from interface import JSONInterface


class SpellResource:
    def __init__(self, character: c.Character):
        self.character = character

    def cast(self, level: int):
        raise NotImplementedError

    def regain(self, level: int):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


class SpellSlots(SpellResource):
    def __init__(self, character):
        super().__init__(character)
        caster = JSONInterface('class/CASTER.super.class')
        cl = self.character.classes[0]
        if (len(self.character.classes) == 1):
            t = cl.get('/spellcasting/slots')
            if (t is None):
                self.max_spell_slots = []
            lv = self.character.level
        else:
            t = 'full'
            lv = self.character.caster_level
        path = '/max_spell_slots/{}/{}'.format(t, lv)
        self.max_spell_slots = caster.get(path)

    def cast(self, level: int):
        slots = self.character.get("/spellcasting/slots")
        if slots[level] < 1:
            # TODO: genericize LowOnResource to accommodate spells
            raise c.OutOfSpells(self.character, level)
        # Does this actually mutate the list? or does it mutate a copy?
        slots[level] -= 1

    def regain(self, level: int):
        slots = self.character.get("/spellcasting/slots")
        if slots[level] >= self.max_spell_slots[level]:
            raise c.OverflowSpells(self.character, level)
        slots[level] += 1

    def reset(self):
        self.character.set("/spellcasting/slots", self.max_spell_slots)


class SpellPoints(SpellResource):
    def __init__(self, character):
        super().__init__(character)
        caster = JSONInterface('class/CASTER.super.class')
        self.max_points = caster.get('/max_spell_points')
        self.costs = caster.get('/spell_point_cost')

    def cast(self, level: int):
        cost = self.costs[level]
        current = self.character.get('/spellcasting/points')
        if current < cost:
            raise c.OutOfSpells(self.character, level)
        self.character.set('/spellcasting/points', current - cost)

    def regain(self, level: int):
        points = self.costs[level]
        current = self.character.get('/spellcasting/points')
        if points + current > self.max_points:
            raise c.OverflowSpells(self.character, level)
        self.character.set('/spellcasting/points', points + current)

    def reset(self):
        self.character.set('/spellcasting/points', self.max_points)
