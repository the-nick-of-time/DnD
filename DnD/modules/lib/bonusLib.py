from dndice import basic

from . import characterLib as char


class Bonus:
    def __init__(self, field, value):
        self.field = field
        self.value = value


class OwnedBonus(Bonus):
    def __init__(self, field, value, character: 'char.Character'):
        super().__init__(field, value)
        self.owner = character
        self.value = basic(self.owner.parse_vars(self.value))


class Bonuses:
    def __init__(self):
        pass

    def get(self, name, default=None):
        pass
