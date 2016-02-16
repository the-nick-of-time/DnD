"""
Character Manager
Version 1.0 (released 2016-01-09)
Direct all comments, suggestions, etc. at /u/the-nick-of-time
Released under the GNU General Public License version 2, as detailed within
the file LICENSE included in the same directory as this code.

This code uses an .ini file written by the script 'Character Creator.py'. Do
that first.

To use this program, enter the character's name in the relevant entry exactly
as it appears in the title of the .ini file, then hit Enter or press the load
button. This should set everything up for you.

HP SECTION:
    This has several entries in it. You generally don't need to directly change
    any of them except for the bottom one.
    The bottom entry is the change in HP that you wish to take. It can be any
    valid rollable string, as defined in the rolling module. Upon pressing the
    "Alter HP" button, the value in the box is added to your current HP.
    Do note that, to take damage, you need enter a negative value in the box,
    like -4 or -3d6.

ATTACK SECTION:
    To perform attacks, enter the name of the attack (not case-sensitive) into
    the box and then press the ATTACK button or the Enter key.
    The check boxes to the right of the main entry allow you to indicate whether
    you are making the attack with advantage or disadvantage. If both are
    checked, they cancel out.
    The attack and damage bonus entries below the main one are there to indicate
    special bonuses, beyond what is expected. Normally, your attack bonus will
    be equal to your ability modifier + your proficiency bonus + magic bonus on
    your weapon (if any). Your normal damage bonus is your ability modifier (for
    a weapon or a spell with the addAbilityToDamage property)
    These two bonuses can be any rollable string. For instance, if you have a
    bard-heavy group, you could have a +1 on attack rolls and a +1d6+1 on
    damage. This sort of temporary buffs are what these entries are for.

SPELL SECTION:
    This shows what spell slots you have not yet spent.
    When you cast a spell as an attack, this section will respond. For all your
    other spellcasting needs, there are the associated buttons. The + and -
    buttons regain or spend spell slots of that level. The Reset button
    refreshes your spell slots to the maximum, like when you rest and regain all
    spells.
    Note that this has no way of keeping track of sorcery points, ki points, or
    channel divinity uses. I leave that to you.

GENERIC ROLL SECTION:
    This entry accepts any rollable string, and rolls it when you press the
    button.

QUIT:
    Saves and quits. This saves all HP-related numbers, your current level, and
    even all of your abilities (in case those change at all).
"""

import tkinter as tk
import configparser as cp

import libraries.rolling as r
import libraries.tkUtility as util
import libraries.DnDbasic as dnd


def readConfig(s):
    val = s.split(',')
    for i in range(len(val)):
        try:
            val[i] = int(val[i])
        except (ValueError):
            pass
    return val


class main:
    def __init__(self, window):
        self.parent = window
        self.activeCharacter = 0
        self.characterdata = {}

        infospell = tk.Frame(window)
        infospell.grid(row=0, column=0)
        self.info = infosec(infospell, self)
        self.info.grid(0, 0)
        self.spell = spellsec(infospell, self)
        self.spell.grid(0, 1)
        self.abil = abilsec(window, self)
        self.abil.grid(0, 1)
        self.hp = hpsec(window, self)
        self.hp.grid(1, 0)
        self.attack = attacksec(window, self)
        self.attack.grid(1, 1)
        self.roll = rollsec(window, self)
        self.roll.grid(2, 0)
        self.exit = tk.Button(window,
                              text="QUIT",
                              fg="red",
                              command=lambda: self.writequit())
        self.exit.grid(row=3, column=2)

    def pullINFO(self):
        data = self.info.getall()
        return data

    def pullABIL(self):
        data = self.abil.getall()
        return data

    def pullHP(self):
        data = self.hp.getall()
        return data

    def getConfigData(self):
        reader = cp.ConfigParser()
        ini_name = './character/' + self.info.name.get() + '.ini'
        data = {'Attacks': {}}
        try:
            reader.read(ini_name)
        except (KeyError):
            errorWindow = tk.Toplevel()
            tk.Label(
                errorWindow,
                text=
                "There is no .ini file in the character directory\nwith name " +
                ini_name).pack()
            tk.Button(errorWindow,
                      command=errorWindow.destroy,
                      text="OK").pack()
            return None

        for sp in reader['Spells']:
            args = readConfig(reader['Spells'][sp])
            args[-1] = args[-1].replace('$', '\n')
            data['Attacks'][sp] = dnd.spell(*args)
        for wep in reader['Weapons']:
            args = readConfig(reader['Weapons'][wep])
            args[-1] = args[-1].replace('$', '\n')
            data['Attacks'][wep] = dnd.weapon(*args)
        for ab in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
            data[ab] = reader['Character'][ab]
        data['level'] = reader['Character']['level']
        data['caster level'] = reader['Character']['caster level']
        data['class'] = reader['Character']['class']
        data['max HP'] = reader['HP']['max hp']
        data['HP'] = reader['HP']['current hp']
        data['temp HP'] = reader['HP']['current temp hp']
        data['spell slots'] = reader['Spell Slots']['spell slots']
        self.characterdata['Attacks'] = data['Attacks']
        try:
            self.characterdata['spell slots'] = r.readList(data['spell slots'],
                                                           mode='int')
        except (SyntaxError):
            self.characterdata['spell slots'] = [0]
        return data

    def pushConfigData(self):
        data = self.getConfigData()
        if (data):
            for sec in [self.info, self.hp, self.abil]:
                sec.populateFromConfig(data)
        self.abil.calcModifiers()

    def initCharacter(self):
        abils = self.pullABIL()
        info = self.pullINFO()
        self.activeCharacter = dnd.character(
            info['name'], int(info['level']), abils,
            self.characterdata['Attacks'], info['class'],
            int(info['caster level']), self.characterdata['spell slots'])
        self.spell.draw()

    def writequit(self):
        data = {}
        data.update(self.pullABIL())
        data.update(self.pullINFO())
        data.update(self.pullHP())
        writer = cp.ConfigParser()
        writer.read('./character/' + data['name'] + '.ini')
        writer['HP']['current hp'] = str(data['HP'])
        writer['HP']['current temp hp'] = str(data['temp HP'])
        writer['HP']['max hp'] = str(data['max HP'])
        writer['Spell Slots']['spell slots'] = str(
            self.activeCharacter.spellslots)
        writer['Character']['level'] = str(self.activeCharacter.level)
        writer['Character']['caster level'] = str(
            self.activeCharacter.casterLevel)
        for val in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
            writer['Character'][val] = str(self.activeCharacter.abilities[val])
        with open('./character/' + data['name'] + '.ini', 'w') as configfile:
            writer.write(configfile)
        self.parent.destroy()


class infosec:
    def __init__(self, master, app):
        self.parent = master
        self.top = app
        self.f = tk.Frame(master)
        self.name = util.labeledEntry(self.f, 'Character Name', 0, 0)
        self.name.bind("<Return>", lambda event: self.LOAD())
        self.level = util.labeledEntry(self.f, 'Character Level', 2, 0)
        self.casterLevel = util.labeledEntry(self.f, 'Caster Level', 4, 0)
        self.Class = util.labeledEntry(self.f, 'Class', 6, 0)
        buttons = tk.Frame(self.f)
        buttons.grid(row=8, column=0)
        self.load = tk.Button(buttons,
                              text="Load character\nfrom file",
                              command=lambda: self.LOAD())
        self.load.grid(row=0, column=0)
        self.initialize = tk.Button(buttons,
                                    text="Initialize\ncharacter",
                                    command=lambda: self.INITIALIZE())
        self.initialize.grid(row=0, column=1)

    def LOAD(self):
        self.top.pushConfigData()
        self.INITIALIZE()

    def INITIALIZE(self):
        self.top.initCharacter()

    def getall(self):
        try:
            out = {}
            out["name"] = self.name.get()
            out["level"] = int(self.level.get())
            out["caster level"] = int(self.casterLevel.get())
            out["class"] = self.Class.get()
            return out
        except:
            print("unable to pull info")
            return {}

    def populateFromConfig(self, data):
        util.replaceEntry(self.level, data['level'])
        util.replaceEntry(self.casterLevel, data['caster level'])
        util.replaceEntry(self.Class, data['class'])

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class spellsec:
    def __init__(self, master, app):
        self.parent = master
        self.top = app
        self.f = tk.Frame(master, width=193)
        self.spellDisplays = [tk.Label(self.f) for x in range(10)]
        self.spellInc = [tk.Button(self.f, text='+') for x in range(10)]
        self.spellDec = [tk.Button(self.f, text='-') for x in range(10)]
        self.reset = tk.Button(self.f,
                               text="Reset\nSpells",
                               command=lambda: self.RESET())

    def draw(self):
        char = self.top.activeCharacter
        i = 1
        while (i < len(char.spellslots)):
            self.spellDisplays[i]["text"] = "Spells left of level " + str(
                i) + ": " + str(char.spellslots[i]) + "     "
            self.spellInc[i]["command"] = lambda x=i: self.INC(x)
            self.spellDec[i]["command"] = lambda x=i: self.DEC(x)
            self.spellDisplays[i].grid(row=i, column=0)
            self.spellInc[i].grid(row=i, column=1)
            self.spellDec[i].grid(row=i, column=2)
            i += 1
        self.reset.grid(row=i, column=2)

    def DEC(self, level):
        self.top.activeCharacter.spendSpell(level)
        self.draw()

    def INC(self, level):
        self.top.activeCharacter.recoverSpell(level)
        self.draw()

    def RESET(self):
        self.top.activeCharacter.resetSpells()
        self.draw()

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class abilsec:
    def __init__(self, master, app):
        self.parent = master
        self.f = tk.Frame(master)
        self.calc = tk.Button(self.f,
                              text="Calculate\nModifiers",
                              command=lambda: self.calcModifiers())
        self.calc.grid(row=6, column=2)
        abilitynames = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        self.modlabels = [tk.Label(self.f) for x in range(6)]
        self.entries = []
        for (i, l) in enumerate(abilitynames):
            self.entries.append(util.labeledEntry(self.f,
                                                  l,
                                                  i,
                                                  0,
                                                  orient='h',
                                                  width=4))

    def calcModifiers(self):
        for (i, e) in enumerate(self.entries):
            self.modlabels[i]["text"] = dnd.abilMod(int(e.get()))
            self.modlabels[i].grid(row=i, column=2)

    def getall(self):
        try:
            out = {}
            names = ['str', 'dex', 'con', 'int', 'wis', 'cha']
            for (n, e) in zip(names, self.entries):
                out[n] = int(e.get())
            return out
        except:
            print("unable to pull abilities")
            return {}

    def populateFromConfig(self, data):
        names = ['str', 'dex', 'con', 'int', 'wis', 'cha']
        for (i, name) in enumerate(names):
            util.replaceEntry(self.entries[i], data[name])

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class hpsec:
    def __init__(self, master, app):
        self.parent = master
        self.f = tk.Frame(self.parent, bd=2, relief="sunken")
        self.max = util.labeledEntry(self.f, 'Maximum HP', 0, 0, width=5)
        self.current = util.labeledEntry(self.f, 'Current HP', 0, 1, width=5)
        self.amount = util.labeledEntry(self.f,
                                        'HP Change\nas integer or roll',
                                        2,
                                        0,
                                        width=10,
                                        orient='h')
        self.amount.bind('<Return>', lambda event: self.changeHP(False))
        self.temp = util.labeledEntry(self.f, '+Temporary HP', 0, 2, width=5)
        buttons = tk.Frame(self.f, pady=15)
        buttons.grid(row=2, column=2)
        self.alterHP = tk.Button(buttons,
                                 text='Alter\nHP',
                                 command=lambda: self.changeHP(False))
        self.alterHP.grid(row=0, column=0)
        self.addtemp = tk.Button(buttons,
                                 text='Add to\ntemp HP',
                                 command=lambda: self.changeHP(True))
        self.addtemp.grid(row=0, column=1)

    def changeHP(self, totemp=False):
        amount = r.call(self.amount.get())
        h = int(self.current.get())
        t = int(self.temp.get())
        m = int(self.max.get())
        if (totemp):
            t += amount
        else:
            if (amount < 0):
                if (abs(amount) > t):
                    amount += t
                    t = 0
                    h += amount
                else:
                    t += amount
            else:
                h += amount
                h = m if h > m else h
        util.replaceEntry(self.temp, str(t))
        util.replaceEntry(self.current, str(h))

    def populateFromConfig(self, data):
        util.replaceEntry(self.max, data['max HP'])
        util.replaceEntry(self.current, data['HP'])
        util.replaceEntry(self.temp, data['temp HP'])

    def getall(self):
        try:
            data = {}
            data['HP'] = int(self.current.get())
            data['temp HP'] = int(self.temp.get())
            data['max HP'] = int(self.max.get())
            return data
        except:
            print("unable to pull HP")
            return {}

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class attacksec:
    def __init__(self, master, app):
        self.parent = master
        self.top = app
        self.f = tk.Frame(master, bd=2, relief="sunken")

        self.attack = util.labeledEntry(self.f, 'Attack method', 0, 0)
        self.attack.bind("<Return>", lambda event: self.doAttack())

        self.adv = tk.BooleanVar()
        self.dis = tk.BooleanVar()
        hasAdvantage = tk.Checkbutton(self.f,
                                      text="Advantage?",
                                      variable=self.adv)
        hasAdvantage.grid(row=0, column=1, sticky="w")
        hasDisadvantage = tk.Checkbutton(self.f,
                                         text="Disadvantage?",
                                         variable=self.dis)
        hasDisadvantage.grid(row=1, column=1, sticky="w")

        bonuses = tk.Frame(self.f, pady=5)
        bonuses.grid(row=2, column=0)
        self.attackBonus = util.labeledEntry(bonuses,
                                             "Attack bonus",
                                             0,
                                             0,
                                             orient='h',
                                             width='8')
        self.damageBonus = util.labeledEntry(bonuses,
                                             "Damage bonus",
                                             1,
                                             0,
                                             orient='h',
                                             width='8')

        self.do = tk.Button(self.f,
                            text="ATTACK",
                            command=lambda: self.doAttack())
        self.do.grid(row=2, column=1)

        self.attackResult = tk.Label(self.f)
        self.attackResult.grid(row=3, column=0)
        self.damageResult = tk.Label(self.f)
        self.damageResult.grid(row=4, column=0)
        self.effects = tk.Label(self.f)
        self.effects.grid(row=5, column=0)

    def doAttack(self):
        try:
            res = dnd.resultFormat(self.top.activeCharacter.attacks[
                self.attack.get().casefold()].attack(
                    self.top.activeCharacter, self.adv.get(), self.dis.get(
                    ), self.attackBonus.get(), self.damageBonus.get()))
            self.attackResult["text"] = res[0]
            self.damageResult["text"] = res[1]
            self.effects["text"] = res[2]
            self.top.spell.draw()
        except (KeyError):
            self.attackResult["text"] = "Attack with that name not found."

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class rollsec:
    def __init__(self, master, app):
        self.parent = master
        self.f = tk.Frame(master)
        self.generalRoll = util.labeledEntry(self.f, 'Dice to roll?', 0, 0)
        self.generalRoll.bind("<Return>", lambda event: self.doRoll())
        self.button = tk.Button(self.f,
                                text="ROLL",
                                command=lambda: self.doRoll())
        self.button.grid(row=2, column=1)
        self.result = tk.Label(self.f)
        self.result.grid(row=2, column=0)

    def doRoll(self):
        self.result["text"] = r.call(self.generalRoll.get())

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


#win = tk.Tk()
#app = main(win)
#win.mainloop()
