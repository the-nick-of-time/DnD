"""
Character Creator
Version 1.0 (released 2016-01-09)
Direct all comments, suggestions, etc. at /u/the-nick-of-time
Released under the GNU General Public License version 2, as detailed within
the file LICENSE included in the same directory as this code.

This code writes a .ini file for use by Character Manager.

How to use:
    Fill out the fields on the left and in the abilities section. These are
    largely self-explanatory. Class accepts the names of the classes in the
    Player's Handbook as well as "multiclass". This option is only used to
    determine the spell slots available to you, so if none of these options
    directly apply to you (Eldritch Knight maybe? I've never played one) use
    an equivalent class like Paladin.
    
    Next, fill out weapon and spell creation sections. Leave sections blank to
        use default values.
    Name: is just that
    Damage Dice: base damage done by the attack, like 1d4 or 2d10+6
    Ability used: str, dex, con, int, wis, or cha, the ability used with
        this attack (often class-dependent, but you need to put it in)
    Attacks per Action: how many individual attacks are done with every attack
        action that you take. For instance, the spell Scorching Ray has a 3 for
        this entry. For AoE spells, you probably just want to put as many 
        targets as could reasonably be hit by it. You can always just roll extra
        to make up the difference.
    Magic Bonus (Weapon): A magic bonus to be added to attack and damage rolls.
    Make Attack Roll?: If yes, do an attack roll with each attack. If no, it
        means that the attack automatically hits (for weapon) or instead
        requires a saving throw (spell).
    Saving Throw Type (spell): What save type the target needs to make (like
        Dexterity or Constitution)
    Ammunition (Weapon): Number of pieces of ammunition that the weapon has.
    Add Ability Modifier to Damage (spell): Whether to add your ability mod to
        the damage done by this spell. This is yes or no like the attack roll
        question.
    Spell Level: Self-explanatory
    Additional Information: This is space for some additional notes on the
        attack, to be displayed when you attack.

    After filling out one of these sections, press the associated "Make" button
        to commit this change to memory.
    When you want to save, hit the "Write" button. When you are done and want to
        quit, hit the "Quit" button.

    To edit one of the spell or weapon entries during the same session, fill out
        the section with the correct information and hit the "Make" button. As
        long as the name is entered the same, it will overwrite the old entry.

    If editing later, you will want to use the "Read" button after entering the
        name to reopen the file. Otherwise, the old data will be discarded
        entirely. This also allows you to edit individual entries as if it was
        in the same session as you made it.
"""

import tkinter as tk
import configparser as cp
import os

import libraries.rolling as r
import libraries.tkUtility as util


class main:
    def __init__(self, win):
        self.master = win
        self.info = infosec(win, self)
        self.info.grid(0, 0)
        self.abil = abilsec(win, self)
        self.abil.grid(0, 1)
        self.weapon = weaponsec(win, self)
        self.weapon.grid(0, 2)
        self.spell = spellsec(win, self)
        self.spell.grid(0, 3)

        buttons = tk.Frame(win)
        buttons.grid(row=0, column=4)
        self.read = tk.Button(buttons,
                              text="Read",
                              command=lambda: self.READ())
        self.read.grid(row=0, column=0)
        self.write = tk.Button(buttons,
                               text="Write",
                               command=lambda: self.WRITE(),
                               fg="green")
        self.write.grid(row=1, column=0)
        self.quit = tk.Button(buttons,
                              text="Quit",
                              command=lambda: self.QUIT(),
                              fg="red")
        self.quit.grid(row=2, column=0)

        self.main = cp.ConfigParser()
        self.main['Character'] = {}
        self.main['Spells'] = {}
        self.main['Weapons'] = {}
        self.main['HP'] = {}
        self.main['Spell Slots'] = {}

    def READ(self):
        try:
            self.main.read('./character/' + self.info.name.get() + '.ini')
        except:
            print("File not found.")
        self.info.populateFromConfig(self.main)

    def WRITE(self):
        info = self.info.pull()
        direc = "./character/"
        if (not os.path.exists(direc)):
            os.mkdir(direc)

        if (info['name']):
            self.main['HP']['max hp'] = info['max hp']
            self.main['HP']['current hp'] = info['max hp']
            self.main['HP']['current temp hp'] = '0'
            self.main['Character']['name'] = info['name']
            self.main['Character']['level'] = info['level']
            self.main['Character']['caster level'] = info['caster level']
            self.main['Character']['class'] = info['class']
            self.main['Character'].update(self.abil.pull())
            self.main['Spell Slots']['spell slots'] = ''
            self.weapon.build()
            self.spell.build()
            with open(direc + info['name'] + '.ini', 'w') as file:
                self.main.write(file)

    def QUIT(self):
        self.WRITE()
        self.master.destroy()


class infosec:
    def __init__(self, parent, app):
        self.f = tk.Frame(parent)
        self.name = util.labeledEntry(self.f, "Character Name", 0, 0)
        self.level = util.labeledEntry(self.f, "Level", 2, 0)
        self.casterlevel = util.labeledEntry(self.f, "Caster Level", 4, 0)
        self.Class = util.labeledEntry(self.f, "Class", 6, 0)
        self.maxhp = util.labeledEntry(self.f, "Maximum HP", 8, 0)

    def pull(self):
        data = {}
        data['name'] = self.name.get()
        data['level'] = (self.level.get())
        data['caster level'] = (self.casterlevel.get())
        data['class'] = self.Class.get().lower()
        data['max hp'] = str(r.call(self.maxhp.get()))
        return data

    def populateFromConfig(self, data):
        util.replaceEntry(self.name, data['Character']['name'])
        util.replaceEntry(self.level, data['Character']['level'])
        util.replaceEntry(self.casterlevel, data['Character']['caster level'])
        util.replaceEntry(self.Class, data['Character']['class'])
        util.replaceEntry(self.maxhp, data['HP']['max hp'])

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class abilsec:
    def __init__(self, parent, app):
        self.f = tk.Frame(parent)
        self.names = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        self.entries = []
        for (i, n) in enumerate(self.names):
            self.entries.append(util.labeledEntry(self.f,
                                                  n,
                                                  i * 2,
                                                  0,
                                                  orient='h',
                                                  width=4))

    def pull(self):
        data = {}
        for (i, n) in enumerate(self.names):
            data[n.lower()] = (self.entries[i].get())
        return data

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class weaponsec:
    def __init__(self, parent, app):
        self.top = app
        self.f = tk.Frame(parent)
        self.name = util.labeledEntry(self.f, "Weapon Name", 2, 0)
        self.dice = util.labeledEntry(self.f, "Damage Dice", 4, 0)
        self.abil = util.labeledEntry(self.f, "Ability Used", 6, 0)
        self.mult = util.labeledEntry(self.f, "Attacks per Action", 8, 0)
        self.magi = util.labeledEntry(self.f, "Magic Bonus", 10, 0)
        self.roll = util.labeledEntry(self.f, "Make Attack Roll?", 12, 0)
        self.ammo = util.labeledEntry(self.f, "Ammunition", 14, 0)
        self.effc = util.labeledEntry(self.f, "Additional Information", 16, 0)
        self.make = tk.Button(self.f,
                              text='Make',
                              command=lambda: self.build())
        self.make.grid(row=18, column=0)
        self.menu = tk.OptionMenu(self.f, self.toEdit, 
                                  *self.top.main.options("Weapons"))
        self.menulabel = tk.Label(self.f, text="Entry to edit")
        self.menulabel.grid(row=0, column=1)
        self.menu.grid(row=1, column=0)

    def build(self):
        s = ''
        defaults = ['0', 'str', '1', '0', '1', '-1', '']
        entries = [self.dice, self.abil, self.mult, self.magi, self.roll,
                   self.ammo, self.effc]
        for (i, entry) in enumerate(entries):
            content = entry.get()
            if (i == 4):
                if (content.lower() == 'no' or content.lower() == 'false'):
                    content = '0'
                else:
                    content = '1'
            if (i >= 2):
                if (content == ''):
                    content = defaults[i]
            if (i == len(entries) - 1):
                content = content.replace('\n', '$')
            s += content + ','
        s = s[:-1]  #cut the trailing ','
        if (self.name.get()):
            new = {self.name.get().lower(): s}
            self.top.main['Weapons'].update(new)

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class spellsec:
    def __init__(self, parent, app):
        self.top = app
        self.f = tk.Frame(parent)
        self.name = util.labeledEntry(self.f, "Spell Name", 2, 0)
        self.level = util.labeledEntry(self.f, "Spell Level", 4, 0)
        self.abil = util.labeledEntry(self.f, "Ability Used", 6, 0)
        self.dice = util.labeledEntry(self.f, "Damage Dice", 8, 0)
        self.addabil = util.labeledEntry(
            self.f, "Add Ability Modifier\nto Damage?", 10, 0)
        self.roll = util.labeledEntry(self.f, "Make Attack Roll?", 12, 0)
        self.save = util.labeledEntry(
            self.f, "Saving Throw Type\n(If Applicable)", 14, 0)
        self.mult = util.labeledEntry(self.f, "Attacks per Action", 16, 0)
        self.effects = util.labeledEntry(self.f, "Additional Information", 18,
                                         0)
        self.make = tk.Button(self.f,
                              text='Make',
                              command=lambda: self.build())
        self.make.grid(row=20, column=0)
        self.toEdit = tk.StringVar()
        self.menu = tk.OptionMenu(self.f, self.toEdit, 
                                  *self.top.main.options("Spells"))
        self.menulabel = tk.Label(self.f, text="Entry to edit")
        self.menulabel.grid(row=0, column=1)
        self.menu.grid(row=1, column=0)

    def build(self):
        s = ''
        defaults = ['-1', 'wis', '0', '0', '0', '', '1', '']
        entries = [self.level, self.abil, self.dice, self.addabil, self.roll,
                   self.save, self.mult, self.effects]
        for (i, entry) in enumerate(entries):
            content = entry.get()
            if (i == 3 or i == 4):
                if (content.lower() == 'no' or content.lower() == 'false'):
                    content = '0'
                else:
                    content = '1'
            if (i >= 3):
                if (content == ''):
                    content = defaults[i]
            if (i == len(entries) - 1):
                content = content.replace('\n', '$')
            s += content + ','
        s = s[:-1]  #cut the trailing ','
        if (self.name.get()):
            new = {self.name.get().lower(): s}
            self.top.main['Spells'].update(new)

    def grid(self, row, column):
        self.f.grid(row=row, column=column)
       
    def populateFromConfig(self):
        which = self.menu.get()
        if
        

#window = tk.Tk()
#app = toplevel(window)
#window.mainloop()
