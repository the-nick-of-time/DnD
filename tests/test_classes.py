import unittest
from pathlib import Path

import DnD.modules.lib.classLib as cl
import DnD.modules.lib.interface as iface

iface.JsonInterface.OBJECTSPATH = Path('../DnD/objects')


class MockCharacter:
    def __init__(self, settings):
        self.settings = settings


class MockSettings:
    def __init__(self, proficiencyDice):
        self.proficiencyDice = proficiencyDice


class TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.base = {
            'class': 'Fighter',
            'level': 2
        }
        self.sub = {
            'class': 'Fighter',
            'level': 3,
            'subclass': 'Champion'
        }
        self.caster = {
            'class': 'Wizard',
            'level': 1
        }
        self.subCaster = {
            'class': 'Fighter',
            'level': 3,
            'subclass': 'Eldritch Knight'
        }

    def test_initialize(self):
        base = cl.Class(self.base)
        self.assertEqual(base.name, 'Fighter')
        self.assertEqual(base.level, 2)
        self.assertEqual(list(base.interface.searchpath.keys()),
                         [str(iface.JsonInterface.OBJECTSPATH / 'class/ALL.super.class'),
                          str(iface.JsonInterface.OBJECTSPATH / 'class/Fighter.class')])

        caster = cl.Class(self.caster)
        self.assertEqual(caster.name, 'Wizard')
        self.assertEqual(caster.level, 1)
        self.assertEqual(list(caster.interface.searchpath.keys()),
                         [str(iface.JsonInterface.OBJECTSPATH / 'class/ALL.super.class'),
                          str(iface.JsonInterface.OBJECTSPATH / 'class/CASTER.super.class'),
                          str(iface.JsonInterface.OBJECTSPATH / 'class/Wizard.class')])

        sub = cl.Class(self.sub)
        self.assertEqual(sub.name, 'Fighter')
        self.assertEqual(sub.level, 3)
        self.assertEqual(list(sub.interface.searchpath.keys()),
                         [str(iface.JsonInterface.OBJECTSPATH / 'class/ALL.super.class'),
                          str(iface.JsonInterface.OBJECTSPATH / 'class/Fighter.class'),
                          str(iface.JsonInterface.OBJECTSPATH / 'class/Fighter.Champion.sub.class')])

    def test_HD(self):
        base = cl.Class(self.base)
        self.assertEqual(base.HD, '1d10')

        wiz = cl.Class(self.caster)
        self.assertEqual(wiz.HD, '1d6')

    def test_caster_level(self):
        base = cl.Class(self.base)
        self.assertEqual(base.casterLevel, 0)
        wiz = cl.Class(self.caster)
        self.assertEqual(wiz.casterLevel, 1)
        wiz.level = 10
        self.assertEqual(wiz.casterLevel, 10)

        sub = cl.Class(self.subCaster)
        self.assertEqual(sub.casterLevel, 1)
        sub.level = 9
        self.assertEqual(sub.casterLevel, 3)

    def test_caster_type(self):
        base = cl.Class(self.base)
        self.assertEqual(base.casterType, cl.CasterType.NONCASTER)

        wiz = cl.Class(self.caster)
        self.assertEqual(wiz.casterType, cl.CasterType.FULL)

        sub = cl.Class(self.subCaster)
        self.assertEqual(sub.casterType, cl.CasterType.THIRD)


class TestClasses(unittest.TestCase):
    def setUp(self) -> None:
        self.base = {
            'class': 'Fighter',
            'level': 2
        }
        self.sub = {
            'class': 'Fighter',
            'level': 3,
            'subclass': 'Champion'
        }
        self.caster = {
            'class': 'Wizard',
            'level': 1
        }
        self.subCaster = {
            'class': 'Fighter',
            'level': 3,
            'subclass': 'Eldritch Knight'
        }
        self.halfCaster = {
            'class': 'Ranger',
            'level': 2
        }
        self.highHd = {
            'class': 'Paladin',
            'level': 3
        }

    def test_index(self):
        singleClass = iface.DataInterface([self.base])
        single = cl.Classes(singleClass)
        self.assertEqual(len(single.classes), 1)
        baseclass = single.classes[0]
        self.assertIs(single[0], baseclass)
        with self.assertRaises(IndexError):
            _ = single[2]
        self.assertIs(single['Fighter'], baseclass)
        with self.assertRaises(KeyError):
            _ = single['Wizard']
        with self.assertRaises(KeyError):
            _ = single[None]

        multiClass = iface.DataInterface([self.base, self.caster])
        multi = cl.Classes(multiClass)
        base = multi.classes[0]
        caster = multi.classes[1]
        self.assertIs(multi[1], caster)
        with self.assertRaises(IndexError):
            _ = multi[2]
        self.assertIs(multi['Fighter'], base)
        self.assertIs(multi['Wizard'], caster)
        with self.assertRaises(KeyError):
            _ = multi['Paladin']

    def test_casterLevel(self):
        nonCaster = iface.DataInterface([self.base])
        non = cl.Classes(nonCaster)
        self.assertEqual(non.casterLevel, 0)

        subCaster = iface.DataInterface([self.subCaster])
        sub = cl.Classes(subCaster)
        self.assertEqual(sub.casterLevel, 1)

        fullCaster = iface.DataInterface([self.caster])
        full = cl.Classes(fullCaster)
        self.assertEqual(full.casterLevel, 1)

        multiClass = iface.DataInterface([self.base, self.caster])
        multi = cl.Classes(multiClass)
        self.assertEqual(multi.casterLevel, 1)

    def test_casterType(self):
        nonCaster = iface.DataInterface([self.base])
        non = cl.Classes(nonCaster)
        self.assertEqual(non.casterType, cl.CasterType.NONCASTER)

        subCaster = iface.DataInterface([self.subCaster])
        sub = cl.Classes(subCaster)
        self.assertEqual(sub.casterType, cl.CasterType.THIRD)

        fullCaster = iface.DataInterface([self.caster])
        full = cl.Classes(fullCaster)
        self.assertEqual(full.casterType, cl.CasterType.FULL)

        multiClass = iface.DataInterface([self.subCaster, self.halfCaster])
        multi = cl.Classes(multiClass)
        self.assertEqual(multi.casterType, cl.CasterType.FULL)

    def test_level(self):
        singleClass = iface.DataInterface([self.base])
        single = cl.Classes(singleClass)
        self.assertEqual(single.level, 2)

        multiClass = iface.DataInterface([self.base, self.halfCaster])
        multi = cl.Classes(multiClass)
        self.assertEqual(multi.level, 4)

    def test_maxHD(self):
        singleClass = iface.DataInterface([self.base])
        single = cl.Classes(singleClass)
        self.assertEqual(single.maxHD, {'1d10': 2})

        equalClass = iface.DataInterface([self.base, self.highHd])
        single = cl.Classes(equalClass)
        self.assertEqual(single.maxHD, {'1d10': 5})

        multiClass = iface.DataInterface([self.base, self.caster])
        different = cl.Classes(multiClass)
        self.assertEqual(different.maxHD, {'1d10': 2, '1d6': 1})

    def test_saveProficiencies(self):
        singleClass = iface.DataInterface([self.base])
        single = cl.Classes(singleClass)
        self.assertEqual(single.saveProficiencies,
                         [cl.abil.AbilityName.STRENGTH, cl.abil.AbilityName.CONSTITUTION])

        multiClass = iface.DataInterface([self.base, self.caster])
        different = cl.Classes(multiClass)
        self.assertEqual(different.saveProficiencies,
                         [cl.abil.AbilityName.STRENGTH, cl.abil.AbilityName.CONSTITUTION])


class TestOwnedClasses(unittest.TestCase):
    def setUp(self) -> None:
        self.base = {
            'class': 'Fighter',
            'level': 2
        }
        self.sub = {
            'class': 'Fighter',
            'level': 3,
            'subclass': 'Champion'
        }
        self.caster = {
            'class': 'Wizard',
            'level': 1
        }
        self.subCaster = {
            'class': 'Fighter',
            'level': 3,
            'subclass': 'Eldritch Knight'
        }
        self.halfCaster = {
            'class': 'Ranger',
            'level': 2
        }
        self.highHd = {
            'class': 'Paladin',
            'level': 3
        }

    def test_proficiency(self):
        bonusChar = MockCharacter(MockSettings(False))
        bonus = cl.OwnedClasses(iface.DataInterface([self.caster]), bonusChar)
        self.assertEqual(bonus.proficiency, 2)
        bonus[0].level = 5
        self.assertEqual(bonus.proficiency, 3)
        bonus[0].level = 9
        self.assertEqual(bonus.proficiency, 4)
        bonus[0].level = 13
        self.assertEqual(bonus.proficiency, 5)
        bonus[0].level = 17
        self.assertEqual(bonus.proficiency, 6)

        diceChar = MockCharacter(MockSettings(True))
        dice = cl.OwnedClasses(iface.DataInterface([self.caster]), diceChar)
        self.assertEqual(dice.proficiency, '1d4')
        dice[0].level = 5
        self.assertEqual(dice.proficiency, '1d6')
        dice[0].level = 9
        self.assertEqual(dice.proficiency, '1d8')
        dice[0].level = 13
        self.assertEqual(dice.proficiency, '1d10')
        dice[0].level = 17
        self.assertEqual(dice.proficiency, '1d12')


if __name__ == '__main__':
    unittest.main()
