class MyError(Exception):
    pass


class LowOnResource(MyError):
    def __init__(self, resource):
        self.resource = resource

    def __str__(self):
        formatstr = 'You have no {rs} remaining.'
        return formatstr.format(rs=self.resource.name)


class OutOfSpells(MyError):
    def __init__(self, character, spell):
        self.character = character
        self.spell = spell

    def __str__(self):
        formatstr = '{char} has no spell slots of level {lv} remaining.'
        return formatstr.format(char=self.character.name,
                                lv=(self.spell if isinstance(self.spell, int)
                                    else self.spell.level))


class OutOfItems(MyError):
    def __init__(self, character, name):
        self.character = character
        self.name = name

    def __str__(self):
        formatstr = '{char} has no {item}s remaining.'
        return formatstr.format(char=self.character.name, item=self.name)


class OverflowSpells(MyError):
    def __init__(self, character, spell):
        self.character = character
        self.spell = spell

    def __str__(self):
        formatstr = '{char} has full spell slots of level {lv} already.'
        return formatstr.format(char=self.character.name, lv=self.spell.level)
