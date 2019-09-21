import unittest

import DnD.modules.lib.hpLib as hp
import DnD.modules.lib.interface as iface


def roll(expr):
    if isinstance(expr, int):
        return expr
    if isinstance(expr, str):
        return 4


hp.basic = roll
hp.res.basic = roll


class MockCharacter:
    def __init__(self, settings, conmod=2):
        self.settings = settings
        self.classes = MockClasses()
        self.abilities = {hp.abil.AbilityName.CONSTITUTION: MockAbility(conmod)}

    def parse_vars(self, expr):
        return expr


class MockSettings:
    def __init__(self, healingMode):
        self.healing = healingMode


class MockClasses:
    def __init__(self):
        self.maxHD = {'1d10': 5}


class MockAbility:
    def __init__(self, modifier: int):
        self.modifier = modifier


class TestHP(unittest.TestCase):
    def setUp(self) -> None:
        record = iface.DataInterface({
            "current": 20,
            "max": 30,
            "bonusMax": 5,
            "temp": 10
        })
        self.obj = hp.HP(record)

    def test_current(self):
        self.assertEqual(self.obj.current, 20)
        self.obj.current = 15
        self.assertEqual(self.obj.current, 15)

    def test_baseMax(self):
        self.assertEqual(self.obj.baseMax, 30)
        self.obj.baseMax = 35
        self.assertEqual(self.obj.baseMax, 35)

    def test_bonusMax(self):
        self.assertEqual(self.obj.bonusMax, 5)
        self.obj.bonusMax = 10
        self.assertEqual(self.obj.bonusMax, 10)

    def test_max(self):
        self.assertEqual(self.obj.max, 35)
        self.obj.baseMax = 40
        self.assertEqual(self.obj.max, 45)
        self.obj.bonusMax = 0
        self.assertEqual(self.obj.max, 40)

    def test_temp(self):
        self.assertEqual(self.obj.temp, 10)
        self.obj.temp = 50
        self.assertEqual(self.obj.temp, 50)

    def test_add_temp(self):
        self.obj.add_temp(5)
        self.assertEqual(self.obj.temp, 10)
        self.obj.add_temp(20)
        self.assertEqual(self.obj.temp, 20)

    def test_change(self):
        self.obj.change(5)
        self.assertEqual(self.obj.current, 25)
        self.obj.change(100)
        self.assertEqual(self.obj.current, 35)
        self.obj.change(-5)
        self.assertEqual(self.obj.temp, 5)
        self.assertEqual(self.obj.current, 35)
        self.obj.change(-10)
        self.assertEqual(self.obj.temp, 0)
        self.assertEqual(self.obj.current, 30)
        self.obj.change(-100)
        self.assertEqual(self.obj.current, 0)
        self.obj.bonusMax = 0
        self.obj.change(100)
        self.assertEqual(self.obj.current, 30)


class TestOwnedHD(unittest.TestCase):
    def setUp(self) -> None:
        record = iface.DataInterface({
            'HD': {
                '1d10': {
                    'number': 2
                }
            }
        })
        self.record = record
        slow = MockCharacter(MockSettings(hp.HealingMode.SLOW))
        vanilla = MockCharacter(MockSettings(hp.HealingMode.VANILLA))
        fast = MockCharacter(MockSettings(hp.HealingMode.FAST))
        self.slow = hp.OwnedHD(record.cd('/HD/1d10'), '1d10', slow)
        self.vanilla = hp.OwnedHD(record.cd('/HD/1d10'), '1d10', vanilla)
        self.fast = hp.OwnedHD(record.cd('/HD/1d10'), '1d10', fast)

    # Not really necessary? Just uses the Resource version of the property
    def test_number(self):
        self.assertEqual(self.slow.number, 2)
        self.record.set('/HD/1d10/number', 4)
        self.assertEqual(self.slow.number, 4)

    def test_maxnumber(self):
        self.assertEqual(self.slow.maxnumber, 5)

    def test_use(self):
        gain = self.slow.use()
        self.assertEqual(gain, 6)
        self.assertEqual(self.slow.number, 1)
        self.slow.owner.abilities = {hp.abil.AbilityName.CON: MockAbility(-5)}
        gain = self.slow.use()
        self.assertEqual(gain, 1)
        self.assertEqual(self.slow.number, 0)
        with self.assertRaises(hp.res.LowOnResource):
            self.slow.use()

    def test_rest_slow(self):
        self.slow.rest(hp.RestLength.TURN)
        self.assertEqual(self.slow.number, 2)
        self.slow.rest(hp.RestLength.SHORT)
        self.assertEqual(self.slow.number, 2)
        self.slow.rest(hp.RestLength.LONG)
        self.assertEqual(self.slow.number, 5)
        self.slow.number = 1
        self.slow.rest(hp.RestLength.LONG)
        self.assertEqual(self.slow.number, 4)

    def test_rest_vanilla(self):
        self.vanilla.number = 0
        self.vanilla.rest(hp.RestLength.TURN)
        self.assertEqual(self.vanilla.number, 0)
        self.vanilla.rest(hp.RestLength.SHORT)
        self.assertEqual(self.vanilla.number, 0)
        self.vanilla.rest(hp.RestLength.LONG)
        self.assertEqual(self.vanilla.number, 3)
        self.vanilla.number = 1
        self.vanilla.rest(hp.RestLength.LONG)
        self.assertEqual(self.vanilla.number, 4)

    def test_rest_fast(self):
        self.fast.number = 0
        self.fast.rest(hp.RestLength.TURN)
        self.assertEqual(self.fast.number, 0)
        self.fast.rest(hp.RestLength.SHORT)
        self.assertEqual(self.fast.number, 1)
        self.fast.rest(hp.RestLength.LONG)
        self.assertEqual(self.fast.number, 5)
        self.fast.number = 0
        self.fast.rest(hp.RestLength.LONG)
        self.assertEqual(self.fast.number, 5)


class TestOwnedHP(unittest.TestCase):
    def setUp(self) -> None:
        record = iface.DataInterface({
            "current": 20,
            "max": 30,
            "bonusMax": 5,
            "temp": 10,
            "HD": {
                "1d10": {
                    "number": 1
                }
            }
        })
        slow = MockCharacter(MockSettings(hp.HealingMode.SLOW))
        vanilla = MockCharacter(MockSettings(hp.HealingMode.VANILLA))
        fast = MockCharacter(MockSettings(hp.HealingMode.FAST))
        self.slow = hp.OwnedHP(record, slow)
        self.vanilla = hp.OwnedHP(record, vanilla)
        self.fast = hp.OwnedHP(record, fast)

    def test_use_HD(self):
        self.slow.use_HD('1d10')
        self.assertEqual(self.slow.current, 26)
        self.assertEqual(self.slow.hd['1d10'].number, 0)
        with self.assertRaises(hp.res.LowOnResource):
            self.slow.use_HD('1d10')
        with self.assertRaises(KeyError):
            self.slow.use_HD('1d6')

    def test_rest_slow(self):
        self.slow.rest(hp.RestLength.TURN)
        self.assertEqual(self.slow.current, 20)
        self.assertEqual(self.slow.hd['1d10'].number, 1)
        self.slow.rest(hp.RestLength.SHORT)
        self.assertEqual(self.slow.current, 20)
        self.assertEqual(self.slow.hd['1d10'].number, 1)
        self.slow.rest(hp.RestLength.LONG)
        self.assertEqual(self.slow.current, 20)
        self.assertEqual(self.slow.hd['1d10'].number, 4)
        self.assertEqual(self.slow.temp, 0)

    def test_rest_vanilla(self):
        self.vanilla.rest(hp.RestLength.TURN)
        self.assertEqual(self.vanilla.current, 20)
        self.assertEqual(self.vanilla.hd['1d10'].number, 1)
        self.vanilla.rest(hp.RestLength.SHORT)
        self.assertEqual(self.vanilla.current, 20)
        self.assertEqual(self.vanilla.hd['1d10'].number, 1)
        self.vanilla.rest(hp.RestLength.LONG)
        self.assertEqual(self.vanilla.current, 35)
        self.assertEqual(self.vanilla.hd['1d10'].number, 4)
        self.assertEqual(self.vanilla.temp, 0)

    def test_rest_fast(self):
        self.fast.rest(hp.RestLength.TURN)
        self.assertEqual(self.fast.current, 20)
        self.assertEqual(self.fast.hd['1d10'].number, 1)
        self.fast.rest(hp.RestLength.SHORT)
        self.assertEqual(self.fast.current, 20)
        self.assertEqual(self.fast.hd['1d10'].number, 2)
        self.fast.rest(hp.RestLength.LONG)
        self.assertEqual(self.fast.current, 35)
        self.assertEqual(self.fast.hd['1d10'].number, 5)
        self.assertEqual(self.fast.temp, 0)


if __name__ == '__main__':
    unittest.main()
