class SpellCaster:
    def __init__(self, character):
        # look at character.caster level
        pass

    def cast(self, name):
        # check if name in character.prepared
        # check if spell json file exists
        pass

    def short_rest(self):
        pass

    def long_rest(self):
        pass


class SpellPoints(SpellCaster):
    def __init__(self, character):
        pass


class SpellSlots(SpellCaster):
    slotcost = [0, 2, 3, 5, 6, 7, 9, 10, 11, 13]

    points = [0, 4, 6, 14, 17, 27, 32, 38, 44, 57, 64, 73, 73, 83, 83, 94, 94,
              107, 114, 123, 133]

    maxslot = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 9, 9]

    def __init__(self, character):
        self.character = character
        lv = character.caster_level()
        self.character.spellpoints = points[lv]
        self.character.maxslot = self.maxslot[lv]

    def cast(self, name):
        if self.character.is_prepared(name):
            # get spell object
            # get spell level
            #
            pass


def fetch_spell(name):
    pass
