import unittest

import DnD.modules.lib.abilitiesLib as abil
import DnD.modules.lib.interface as iface


def abilitiesEqual(a: abil.Ability, b: abil.Ability):
    return a.name == b.name and a.score == b.score

abil.Ability.__eq__ = abilitiesEqual


class TestAbility(unittest.TestCase):
    def test_create(self):
        abilities = [abil.Ability(abil.AbilityName.DEX, i) for i in range(1, 21)]
        self.assertEqual(list(map(lambda a: a.score, abilities)),
                         list(range(1, 21)))
        self.assertEqual(abil.Ability(abil.AbilityName.STR, 10).abbreviation, 'STR')
        self.assertEqual(abil.Ability(abil.AbilityName.DEX, 10).abbreviation, 'DEX')
        self.assertEqual(abil.Ability(abil.AbilityName.CON, 10).abbreviation, 'CON')
        self.assertEqual(abil.Ability(abil.AbilityName.INT, 10).abbreviation, 'INT')
        self.assertEqual(abil.Ability(abil.AbilityName.WIS, 10).abbreviation, 'WIS')
        self.assertEqual(abil.Ability(abil.AbilityName.CHA, 10).abbreviation, 'CHA')

    def test_modifier(self):
        abilities = [abil.Ability(abil.AbilityName.DEX, i) for i in range(1, 21)]
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
            abil.AbilityName.STR: abil.Ability(abil.AbilityName.STR, 16),
            abil.AbilityName.DEX: abil.Ability(abil.AbilityName.DEX, 9),
            abil.AbilityName.CON: abil.Ability(abil.AbilityName.CON, 16),
            abil.AbilityName.INT: abil.Ability(abil.AbilityName.INT, 12),
            abil.AbilityName.WIS: abil.Ability(abil.AbilityName.WIS, 20),
            abil.AbilityName.CHA: abil.Ability(abil.AbilityName.CHA, 16),
        })

    def test_get_set(self):
        abilities = abil.Abilities(self.data)
        self.assertEqual(abilities[abil.AbilityName.STR],
                         abil.Ability(abil.AbilityName.STR, 16))
        abilities[abil.AbilityName.STR] = 10
        self.assertEqual(abilities[abil.AbilityName.STR],
                         abil.Ability(abil.AbilityName.STR, 10))


if __name__ == '__main__':
    unittest.main()
