import re
from typing import Optional

from dndice import basic

from . import characterLib as char
from .exceptionsLib import LowOnResource
from .interface import DataInterface
from .settingsLib import RestLength


class Resource:
    def __init__(self, jf: Optional[DataInterface], definition: DataInterface = None):
        self.record = jf
        self.definition = definition or jf
        self.recharge = RestLength.from_string(self.definition.get('/recharge'))
        self.value = self.definition.get('/value')
        self.name = self.definition.get('/name')

    @property
    def number(self):
        return self.record.get('/number')

    @number.setter
    def number(self, value):
        self.record.set('/number', value)

    @property
    def maxnumber(self):
        return self.record.get('/maxnumber') or self.definition.get('/maxnumber')

    @maxnumber.setter
    def maxnumber(self, value):
        self.record.set('/maxnumber', value)

    def use(self, number):
        if self.number < number:
            raise LowOnResource(self)
        self.number -= number
        if isinstance(self.value, str):
            return basic('+'.join([self.value] * number))
        elif isinstance(self.value, int):
            return number * self.value
        else:
            return 0

    def regain(self, number):
        if self.number + number > self.maxnumber:
            self.reset()
        else:
            self.number += number

    def reset(self):
        self.number = self.maxnumber

    def rest(self, length):
        if length >= self.recharge:
            self.reset()
            return self.number
        return -1


class OwnedResource(Resource):
    def __init__(self, jf: DataInterface, character: 'char.Character', definition: DataInterface = None):
        super().__init__(jf, definition)
        self.owner = character
        val = character.parse_vars(self.value)
        if isinstance(val, str):
            # Evaluate parenthetical expressions for ease & clean expression later
            pattern = r'\(.*\)'
            rep = lambda m: str(basic(m.group(0)))
            new = re.sub(pattern, rep, val)
            self.value = new
        else:
            self.value = val

    @property
    def maxnumber(self):
        base = super().maxnumber
        return self.owner.parse_vars(base)
