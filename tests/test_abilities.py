import unittest

import DnD.modules.lib.abilitiesLib as abil
import DnD.modules.lib.interface as iface


def abilitiesEqual(a: abil.Ability, b: abil.Ability):
    return a.name == b.name and a.score == b.score


abil.Ability.__eq__ = abilitiesEqual


class TestAbility(unittest.TestCase):
    def test_create(self):
        dummy = iface.DataInterface({})
        self.assertEqual(abil.Ability(abil.AbilityName.STR, dummy).abbreviation, 'STR')
        self.assertEqual(abil.Ability(abil.AbilityName.DEX, dummy).abbreviation, 'DEX')
        self.assertEqual(abil.Ability(abil.AbilityName.CON, dummy).abbreviation, 'CON')
        self.assertEqual(abil.Ability(abil.AbilityName.INT, dummy).abbreviation, 'INT')
        self.assertEqual(abil.Ability(abil.AbilityName.WIS, dummy).abbreviation, 'WIS')
        self.assertEqual(abil.Ability(abil.AbilityName.CHA, dummy).abbreviation, 'CHA')

    def test_score(self):
        dummy = iface.DataInterface({
            "Strength": 16,
            "Dexterity": 9,
            "Constitution": 16,
            "Intelligence": 12,
            "Wisdom": 20,
            "Charisma": 16
        })
        for i in range(1, 21):
            ability = abil.Ability(abil.AbilityName.DEX, dummy.cd('/Dexterity'))
            ability.score = i
            self.assertEqual(ability.score, i)

    def test_modifier(self):
        abilities = [abil.Ability(abil.AbilityName.DEX, iface.DataInterface({'Dexterity': i}).cd('/Dexterity')) for i in range(1, 21)]
        mods = [-5, -4, -4, -3, -3, -2, -2, -1, -1, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        self.assertEqual(list(map(lambda a: a.modifier, abilities)), mods)


class TestAbilities(unittest.TestCase):
    def setUp(self) -> None:
        self.data = iface.DataInterface({
            "Strength": 16,
            "Dexterity": 9,
            "Constitution": 16,
            "Intelligence": 12,
            "Wisdom": 20,
            "Charisma": 16
        })

    def test_create(self):
        abilities = abil.Abilities(self.data)
        self.assertEqual(abilities.values, {
            abil.AbilityName.STR: abil.Ability(abil.AbilityName.STR, self.data.cd('/Strength')),
            abil.AbilityName.DEX: abil.Ability(abil.AbilityName.DEX, self.data.cd('/Dexterity')),
            abil.AbilityName.CON: abil.Ability(abil.AbilityName.CON, self.data.cd('/Constitution')),
            abil.AbilityName.INT: abil.Ability(abil.AbilityName.INT, self.data.cd('/Intelligence')),
            abil.AbilityName.WIS: abil.Ability(abil.AbilityName.WIS, self.data.cd('/Wisdom')),
            abil.AbilityName.CHA: abil.Ability(abil.AbilityName.CHA, self.data.cd('/Charisma')),
        })

    def test_get_set(self):
        abilities = abil.Abilities(self.data)
        self.assertEqual(abilities[abil.AbilityName.STR],
                         abil.Ability(abil.AbilityName.STR, self.data.cd('/Strength')))
        abilities[abil.AbilityName.STR] = 10
        self.assertEqual(abilities[abil.AbilityName.STR],
                         abil.Ability(abil.AbilityName.STR, self.data.cd('/Strength')))


if __name__ == '__main__':
    unittest.main()
