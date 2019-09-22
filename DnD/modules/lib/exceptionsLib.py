class DnDError(Exception):
    pass


class LowOnResource(DnDError):
    def __init__(self, resource):
        self.resource = resource

    def __str__(self):
        formatstr = 'You have no {rs} remaining.'
        return formatstr.format(rs=self.resource.name)


class OutOfItems(DnDError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        formatstr = 'You have no {item}s remaining.'
        return formatstr.format(item=self.name)


class SpellError(DnDError):
    pass


class OutOfSpells(SpellError):
    def __init__(self, spell):
        self.spell = spell

    def __str__(self):
        formatstr = 'You have no spell slots of level {lv} remaining.'
        return formatstr.format(lv=(self.spell if isinstance(self.spell, int)
                                    else self.spell.level))


class OverflowSpells(SpellError):
    def __init__(self, spell):
        self.spell = spell

    def __str__(self):
        formatstr = 'You have full spell slots of level {lv} already.'
        return formatstr.format(lv=self.spell.level)


class NotARitualError(SpellError):
    pass


class AlreadyPrepared(SpellError):
    pass


class CharacterDead(DnDError):
    pass


class InterfaceError(DnDError):
    pass


class ReadonlyError(InterfaceError):
    pass


class PathError(InterfaceError, ValueError):
    pass


class EquipSlotsFull(DnDError):
    pass


class GuiError(DnDError):
    pass
