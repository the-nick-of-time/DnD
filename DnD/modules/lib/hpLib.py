from math import ceil

from dndice import basic

from . import abilitiesLib as abil
from . import characterLib as char
from . import resourceLib as res
from .interface import DataInterface
from .settingsLib import RestLength, HealingMode


class HP:
    def __init__(self, jf: DataInterface):
        self.record = jf

    @property
    def current(self):
        return self.record.get('/current') or 0

    @current.setter
    def current(self, value):
        if isinstance(value, int):
            if value > 0:
                if value < self.max:
                    self.record.set('/current', value)
                else:
                    self.record.set('/current', self.max)
            else:
                self.record.set('/current', 0)
        else:
            raise TypeError('Trying to set HP to not a number')

    @property
    def max(self):
        return self.baseMax + self.bonusMax

    @property
    def baseMax(self):
        return self.record.get('/max') or 0

    @baseMax.setter
    def baseMax(self, value):
        self.record.set('/max', value)

    @property
    def temp(self):
        return self.record.get('/temp') or 0

    @temp.setter
    def temp(self, value):
        self.record.set('/temp', value)

    @property
    def bonusMax(self):
        return self.record.get('/bonusMax') or 0

    @bonusMax.setter
    def bonusMax(self, value):
        self.record.set('/bonusMax', value)

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


class OwnedHP(HP):
    def __init__(self, jf: DataInterface, character: 'char.Character'):
        super().__init__(jf)
        self.owner = character
        self.hd = {size: OwnedHD(self.record.cd('/HD/' + size), size, character)
                   for size in self.record.get('/HD')}

    def rest(self, length: RestLength):
        if length == RestLength.LONG:
            if self.owner.settings.healing in (HealingMode.VANILLA, HealingMode.FAST):
                self.current = self.max
            self.temp = 0
        for size in self.hd.values():
            size.rest(length)

    def use_HD(self, which: str):
        value = self.hd[which].use()
        self.change(value)


class OwnedHD(res.OwnedResource):
    def __init__(self, jf: DataInterface, size: str, character: 'char.Character'):
        super().__init__(jf, character=character)
        self.name = 'Hit Die'
        self.value = size
        self.recharge = RestLength.LONG

    @property
    def maxnumber(self):
        return self.owner.classes.maxHD[self.value]

    def use(self, number=1):
        # Use the number argument?
        roll = super().use(1)
        conmod = self.owner.abilities[abil.AbilityName.CON].modifier
        return roll + conmod if (roll + conmod > 1) else 1

    def rest(self, length):
        if length == RestLength.LONG:
            if self.owner.settings.healing == HealingMode.FAST:
                self.reset()
            else:
                self.regain(ceil(self.maxnumber / 2))
        elif length == RestLength.SHORT:
            if self.owner.settings.healing == HealingMode.FAST:
                self.regain(self.maxnumber // 4 or 1)
