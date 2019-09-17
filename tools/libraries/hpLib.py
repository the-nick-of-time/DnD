from math import ceil

from dndice import basic

from classes import Character
from exceptionsLib import LowOnResource
from helpers import modifier
from interface import JsonInterface
from resourceLib import Resource
from settingsLib import RestLengths, HealingMode


class HP:
    def __init__(self, character: Character):
        # TODO: take SubInterface for consistency and division of responsibility
        self.owner = character
        self.record = character.record
        self.hd = {size: HD(self.record, size, character) for size in self.record.get('/HP/HD')}

    @property
    def current(self):
        return self.record.get('/HP/current')

    @current.setter
    def current(self, value):
        if isinstance(value, int):
            self.record.set('/HP/current', value)
        else:
            raise TypeError('Trying to set HP to not a number')

    @property
    def max(self):
        return self.record.get('/HP/max')

    @max.setter
    def max(self, value):
        self.record.set('/HP/max', value)

    @property
    def temp(self):
        return self.record.get('/HP/temp')

    @temp.setter
    def temp(self, value):
        self.record.set('/HP/temp', value)

    def change(self, amount):
        """Change the HP

        :param amount: A rollable amount
        :return: The actual change in HP
        """
        delta = basic(amount)
        if delta == 0:
            return 0
        if delta < 0:
            if abs(delta) > self.temp:
                # overflow beyond temp
                delta += self.temp
                self.temp = 0
                self.current += delta
                return delta
            else:
                # Temp absorbs it all
                self.temp += delta
                return 0
        else:
            # healing
            if self.current + delta > self.max:
                delta = self.max - self.current
            self.current += delta
            return delta

    def add_temp(self, amount):
        """Add some temp HP

        :param amount: A rollable amount
        :return: The actual change in HP (always 0 because temp HP is not real)
        """
        delta = basic(amount)
        if delta > self.temp:
            self.temp = delta
        return 0

    def rest(self, length):
        if length == RestLengths.LONG:
            if self.owner.settings.healing in (HealingMode.VANILLA, HealingMode.FAST):
                self.current = self.max
            self.temp = 0
        for size in self.hd.values():
            size.rest(length)


class HD(Resource):
    def __init__(self, jf: JsonInterface, size: str, character: Character):
        super().__init__(jf, '/HP/HD/' + size, character=character)
        self.name = 'Hit Die'
        self.value = size
        self.recharge = RestLengths.LONG

    @property
    def maxnumber(self):
        return self.owner.classes.maxHD[self.value]

    def use(self, _):
        try:
            roll = super().use(1)
        except LowOnResource:
            return 0
        conmod = modifier(self.record.get('/abilities/Constitution'))
        return roll + conmod if (roll + conmod > 1) else 1

    def rest(self, length):
        if length == RestLengths.LONG:
            if self.owner.settings.healing == HealingMode.FAST:
                self.reset()
            else:
                self.regain(ceil(self.maxnumber / 2))
        if length == RestLengths.SHORT:
            if self.owner.settings.healing == HealingMode.FAST:
                self.regain(ceil(self.maxnumber / 4))
