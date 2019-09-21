import unittest
from pathlib import Path

import DnD.modules.lib.interface as iface
import DnD.modules.lib.spellcastingLib as cast
from DnD.modules.lib.settingsLib import RestLength

iface.JsonInterface.OBJECTSPATH = Path('DnD/objects')


class MockCharacter:
    def __init__(self, classes):
        self.classes = classes


class MockClasses:
    def __init__(self, casterLevels, casterTypes):
        self.levels = casterLevels
        self.types = casterTypes
        casterClasses = [t for l, t in zip(self.levels, self.types)
                         if l > 0]
        if len(casterClasses) == 0:
            self.casterType = MockCasterType('none')
        elif len(casterClasses) == 1:
            self.casterType = MockCasterType(casterClasses[0])
        else:
            self.casterType = MockCasterType('full')
        self.casterLevel = sum(casterLevels)


class MockCasterType:
    def __init__(self, typ):
        self.value = typ


class TestSpellSlots(unittest.TestCase):
    def setUp(self) -> None:
        self.data = iface.DataInterface({"slots": [999999, 4, 2, 1]})
        singleCaster = MockClasses([5], ['full'])
        mixedCaster = MockClasses([1, 0], ['full', ''])
        multiCaster = MockClasses([1, 1], ['full', 'full'])
        self.singleCaster = MockCharacter(singleCaster)
        self.mixedCaster = MockCharacter(mixedCaster)
        self.multiCaster = MockCharacter(multiCaster)

    def test_initialize(self):
        slots = cast.OwnedSpellSlots(self.data, self.singleCaster)
        self.assertEqual(slots.max_spell_slots, [999999, 4, 3, 2])
        slots = cast.OwnedSpellSlots(self.data, self.mixedCaster)
        self.assertEqual(slots.max_spell_slots, [999999, 2])
        slots = cast.OwnedSpellSlots(self.data, self.multiCaster)
        self.assertEqual(slots.max_spell_slots, [999999, 3])

    def test_cast(self):
        slots = cast.OwnedSpellSlots(self.data, self.singleCaster)
        slots.cast(3)
        self.assertEqual(self.data.get('/slots/3'), 0)
        with self.assertRaises(cast.OutOfSpells):
            slots.cast(3)
        slots.cast(0)
        self.assertEqual(self.data.get('/slots/0'), 999999)

    def test_regain(self):
        slots = cast.OwnedSpellSlots(self.data, self.singleCaster)
        slots.regain(2)
        self.assertEqual(self.data.get('/slots/2'), 3)
        with self.assertRaises(cast.OverflowSpells):
            slots.regain(2)

    def test_reset(self):
        slots = cast.OwnedSpellSlots(self.data, self.singleCaster)
        slots.reset()
        self.assertEqual(self.data.get('/slots'), [999999, 4, 3, 2])

    def test_rest(self):
        slots = cast.OwnedSpellSlots(self.data, self.singleCaster)
        slots.rest(RestLength.SHORT)
        self.assertEqual(self.data.get('/slots'), [999999, 4, 2, 1])
        slots.rest(RestLength.TURN)
        self.assertEqual(self.data.get('/slots'), [999999, 4, 2, 1])
        slots.rest(RestLength.NOTHING)
        self.assertEqual(self.data.get('/slots'), [999999, 4, 2, 1])
        slots.rest(RestLength.LONG)
        self.assertEqual(self.data.get('/slots'), [999999, 4, 3, 2])


if __name__ == '__main__':
    unittest.main()
