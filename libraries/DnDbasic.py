"""
D&D Basics
Version 1.0 (released 2016-01-09)
Direct all comments, suggestions, etc. at /u/the-nick-of-time
Released under the GNU General Public License version 2, as detailed within
the file LICENSE included in the same directory as this code.

This module contains definitions of D&D-specific objects, for use in the Character manager.

Character represents a standard D&D character. It encapsulates the basic numerical
information about the person, as well as all attacks available to them.

Weapon represents a physical weapon. 

Spell represents any damaging spell. 

You should never have to hardcode one of these objects as all of this will be handled in 
the character creator.

"""

import libraries.rolling as r


def abilMod(score):
    return (score - 10) // 2


class character:
    # yapf disable
    half = [[],
            [999999, 2],
            [999999, 3],
            [999999, 3],
            [999999, 4, 2],
            [999999, 4, 2],
            [999999, 4, 3],
            [999999, 4, 3],
            [999999, 4, 3, 2],
            [999999, 4, 3, 2],
            [999999, 4, 3, 3],
            [999999, 4, 3, 3],
            [999999, 4, 3, 3, 1],
            [999999, 4, 3, 3, 1],
            [999999, 4, 3, 3, 2],
            [999999, 4, 3, 3, 2],
            [999999, 4, 3, 3, 3, 1],
            [999999, 4, 3, 3, 3, 1],
            [999999, 4, 3, 3, 3, 2],
            [999999, 4, 3, 3, 3, 2]]
    full = [[999999, 2],
            [999999, 3],
            [999999, 4, 2],
            [999999, 4, 3],
            [999999, 4, 3, 2],
            [999999, 4, 3, 3],
            [999999, 4, 3, 3, 1],
            [999999, 4, 3, 3, 2],
            [999999, 4, 3, 3, 3, 1],
            [999999, 4, 3, 3, 3, 2],
            [999999, 4, 3, 3, 3, 2, 1],
            [999999, 4, 3, 3, 3, 2, 1],
            [999999, 4, 3, 3, 3, 2, 1, 1],
            [999999, 4, 3, 3, 3, 2, 1, 1],
            [999999, 4, 3, 3, 3, 2, 1, 1, 1],
            [999999, 4, 3, 3, 3, 2, 1, 1, 1],
            [999999, 4, 3, 3, 3, 2, 1, 1, 1, 1],
            [999999, 4, 3, 3, 3, 3, 1, 1, 1, 1],
            [999999, 4, 3, 3, 3, 3, 2, 1, 1, 1],
            [999999, 4, 3, 3, 3, 3, 2, 2, 1, 1]]
    warlock = [[999999, 1],
               [999999, 2],
               [999999, 0, 2],
               [999999, 0, 2],
               [999999, 0, 0, 2],
               [999999, 0, 0, 2],
               [999999, 0, 0, 0, 2],
               [999999, 0, 0, 0, 2],
               [999999, 0, 0, 0, 0, 2],
               [999999, 0, 0, 0, 0, 2],
               [999999, 0, 0, 0, 0, 3],
               [999999, 0, 0, 0, 0, 3],
               [999999, 0, 0, 0, 0, 3],
               [999999, 0, 0, 0, 0, 3],
               [999999, 0, 0, 0, 0, 3],
               [999999, 0, 0, 0, 0, 3],
               [999999, 0, 0, 0, 0, 4],
               [999999, 0, 0, 0, 0, 4],
               [999999, 0, 0, 0, 0, 4],
               [999999, 0, 0, 0, 0, 4]]
    # yapf enable
    cantrips = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4]
    proficiency = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6]

    def __init__(self,
                 name,
                 level,
                 abilities,
                 attacks={},
                 Class='multiclass',
                 casterLevel=0,
                 spellSlots=[]):
        #name: string
        #level: integer [1-20], total level of your character
        #abilities: dict, string ABILNAME: int SCORE
        #attacks: dict, string NAME: spell or weapon ATTACK
        #casterType: string, half, full, or warlock
        #casterLevel: integer [1-20], caster level of character
        #spellSlots: list length 10, ordered list of unused spell slots of each level
        self.name = name
        self.level = level
        self.abilities = abilities
        self.attacks = attacks
        if (Class == 'bard' or Class == 'cleric' or Class == 'druid' or
                Class == 'sorcerer' or Class == 'wizard' or
                Class == 'multiclass'):
            self.casterType = 'full'
        elif (Class == 'paladin' or Class == 'ranger'):
            self.casterType = 'half'
        elif (Class == 'warlock'):
            self.casterType = 'warlock'
        else:
            self.casterType = ''

        self.casterLevel = casterLevel
        self.spellslots = spellSlots
        self.cantripscale = self.cantrips[casterLevel - 1]
        self.proficiencyBonus = self.proficiency[level - 1]

    def resetSpells(self):
        if (self.casterType == 'full'):
            self.spellslots = self.full[self.casterLevel - 1]
        elif (self.casterType == 'half'):
            self.spellslots = self.half[self.casterLevel - 1]
        elif (self.casterType == 'warlock'):
            self.spellslots = self.warlock[self.casterLevel - 1]
        else:
            self.spellslots = [0]

    def spendSpell(self, level):
        self.spellslots[level] -= 1

    def recoverSpell(self, level):
        self.spellslots[level] += 1


class spell:
    def __init__(self,
                 level,
                 ability,
                 damageDice,
                 addAbilToDamage=False,
                 attackRoll=False,
                 savingthrowtype='',
                 multipleAttack=1,
                 effects=''):
        #level: int [1-9], spell level
        #ability: string ['str','dex','con','int','wis','cha'], the ability used by the spell
        #damageDice: string, a rollable string that is the base damage done
        #addAbilToDamage: bool, whether to add the ability modifier to the damage done
        #attackRoll: bool, whether to make an attack roll (False is save)
        #savingthrowtype: string, what type of
        self.level = level
        self.ability = ability
        self.damagedice = damageDice
        self.addabiltodamage = addAbilToDamage
        self.attackroll = attackRoll
        self.savetype = savingthrowtype
        self.multiple = multipleAttack
        self.effects = effects

    def attack(self, character, adv, dis, attackBonus, damageBonus):
        modifier = abilMod(character.abilities[self.ability])
        result = [[], [], '']
        if (character.spellslots[self.level] == 0):
            result = [[], [], 'You are out of spells of that level.']
            return result
        elif (self.level > 0):
            character.spendSpell(self.level)
        for all in range(self.multiple):
            opt = 'execute'
            if (self.attackroll):
                if (adv and not dis):
                    attackstring = '2d20h1'
                elif (not adv and dis):
                    attackstring = '2d20l1'
                else:
                    attackstring = '1d20'
                AB = r.call(
                    attackBonus) + character.proficiencyBonus + modifier
                attackresult = r.call(attackstring)
                if (attackresult == 1):
                    result[0].append('Miss')
                    opt = 'zero'
                elif (attackresult == 20):
                    result[0].append('Critical')
                    opt = 'critical'
                else:
                    result[0].append(attackresult + AB)
                    opt = 'execute'
            DB = r.call(damageBonus,
                        option=opt) + (modifier if self.addabiltodamage else 0)
            if (self.level == 0):
                dice = self.damagedice + ('+' + self.damagedice) * (
                    character.cantripscale - 1)
            else:
                dice = self.damagedice
            result[1].append(r.call(dice, option=opt, modifiers=DB))
        if (not self.attackroll):
            saveDC = 8 + character.proficiencyBonus + modifier
            result[0] = ('Make a DC ' + str(saveDC) + ' ' + self.savetype +
                         ' saving throw.')
        result[2] = self.effects
        return result


class weapon:
    def __init__(self,
                 damageDice,
                 ability,
                 multipleAttack=1,
                 magicBonus=0,
                 attackRoll=True,
                 ammunition=-1,
                 effects=''):
        #damageDice: string, rollable string of base damage
        #ability: string ['str','dex','con','int','wis','cha'], the ability used by the weapon
        #damageDice: string, a rollable string that is the base damage done
        #multipleAttack: int, how many attacks are done in one attack action
        #magicBonus: int, magic bonus that applies to attack and damage
        #attackRoll: bool, whether to make an attack roll (if False, attack is assumed to autohit
        #ammunition: int, how much ammunition there is for this weapon (-1 for infinite/does not use ammunition)
        #effects: string, whatever extra effects the weapon has
        self.damagedice = damageDice
        self.multiple = multipleAttack
        self.attackroll = attackRoll
        self.ammunition = ammunition
        self.effects = effects
        self.ability = ability
        self.magicbonus = magicBonus

    def attack(self, character, adv, dis, attackBonus, damageBonus):
        result = [[], [], '']
        modifier = abilMod(character.abilities[self.ability])
        if (self.ammunition == 0):
            result = [[], [], 'You are out of ammunition for this weapon.']
            return result
        if (self.ammunition):
            self.ammunition -= 1
        for all in range(self.multiple):
            opt = 'execute'
            if (self.attackroll):
                if (adv and not dis):
                    attackstring = '2d20h1'
                elif (not adv and dis):
                    attackstring = '2d20l1'
                else:
                    attackstring = '1d20'
                AB = r.call(
                    attackBonus) + character.proficiencyBonus + modifier + self.magicbonus
                attackresult = r.call(attackstring)
                if (attackresult == 1):
                    result[0].append('Miss')
                    opt = 'zero'
                elif (attackresult == 20):
                    result[0].append('Critical')
                    opt = 'critical'
                else:
                    result[0].append(attackresult + AB)
                    option = 'execute'
            DB = r.call(damageBonus, option=opt) + modifier + self.magicbonus
            result[1].append(r.call(self.damagedice, option=opt, modifiers=DB))
        if (not self.attackroll):
            result[0] = 'Attack auto-hits.'
        result[2] = self.effects
        return result


def resultFormat(result):
    out = ['', '', '']
    if (type(result[0]) is str):
        out[0] = result[0]
    else:
        out[0] = 'Attack Result: '
        for a in result[0]:
            out[0] += (str(a) + ', ')
        out[0] = out[0][:-2]  #cut off trailing ', '
    out[1] = 'Damage Done: '
    for d in result[1]:
        out[1] += str(d) + ', '
    out[1] = out[1][:-2]  #cut off trailing ', '

    out[2] = result[2]  #effects

    return out
