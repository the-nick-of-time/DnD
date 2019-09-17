import re

from dndice import basic

from characterLib import Character
from exceptionsLib import LowOnResource
from interface import JSONInterface
from settingsLib import RestLengths


class Resource:
    def __init__(self, jf: JSONInterface, path: str, defjf=None, defpath=None):
        self.record = jf
        self.path = path
        self.value = self._get('value')
        self.recharge = RestLengths.from_string(self._get('recharge'))
        self.definition = defjf if defjf is not None else jf
        self.defpath = defpath if defpath is not None else path
        self.name = self._def_get('name')

    def _get(self, path):
        return self.record.get(self.path + '/' + path)

    def _set(self, path, value):
        self.record.set(self.path + '/' + path, value)

    def _def_get(self, path):
        return self.definition.get(self.defpath + '/' + path)

    @property
    def number(self):
        return self._get('number')

    @number.setter
    def number(self, value):
        self._set('number', value)

    @property
    def maxnumber(self):
        val = self._get('maxnumber')
        if val is not None:
            if self.owner is not None:
                return self.owner.parse_vars(val)
            return val
        if self.owner is not None:
            mx = self._def_get('maxnumber')
            return self.owner.parse_vars(mx)
        return self._def_get('maxnumber')

    @maxnumber.setter
    def maxnumber(self, value):
        self.record.set(self.path + '/maxnumber', value)

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
    def __init__(self, jf: JSONInterface, path: str, character: Character, defjf=None, defpath=None):
        super().__init__(jf, path, defjf, defpath)
        self.owner = character
        val = character.parse_vars(self.value, mathIt=False)
        if isinstance(val, str):
            pattern = r'\(.*\)'
            rep = lambda m: str(basic(m.group(0)))
            new = re.sub(pattern, rep, val)
            self.value = new
        else:
            self.value = val
