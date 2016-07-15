"""
Monster Manager
Version 1.0 (released 2016-01-09)
Direct all comments, suggestions, etc. at /u/the-nick-of-time
Released under the GNU General Public License version 2, as detailed within
the file LICENSE included in the same directory as this code.

This tool coordinates all of the actors in a combat, with simple functions that
allow the monsters to perform attacks.

The first thing for you to do is press the "New Monster" button to open the
dialog. This will create a popup window with a variety of fields that can be
filled out. Fill them with relevant information and hit the "Finish" button.

The main window will now contain a section that contains relevant information
about the monster. From here, you can make the monster take damage (by inserting
a negative value in the "Change HP" entry and pressing the button), recover HP
(same but positive), or perform attacks. This aspect perhaps bears explanation.
To perform an attack, fill out the attack bonus and damage done and press the
button. The attack bonus is **added to the d20 roll**, and can be any valid
rollable string. This includes simple integers as well as dice, arithmetic
expressions, and even comparisons. Also ridiculous expressions like "1d4d4d4d4".

If you need to roll dice for any other reason, there is a section that has just
an entry and a button.

I recommend creating all the monsters first and then the characters. This
ensures that the copy feature works correctly. However, it won't break anything
if you add monsters after characters.
"""

import tkinter as tk
import libraries.rolling as r
import libraries.tkUtility as util


def modifier(score):
    return (score - 10) // 2


def all_children(frame):
    return childrenrecursive(frame)


def childrenrecursive(current):
    l = []
    for c in current.winfo_children():
        l.extend(childrenrecursive(c))
    l.append(current)
    return l


class monster:
    def __init__(self, name, HP, HD, init, AC, abilities):
        #name: string, name of monster
        #HP: integer, starting HP of monster
        #HD: string, rollable string of hit dice
        #init: integer, initiative value of the monster
        #AC: string or integer, AC of monster
        #abilities: list, ordered list of scores [str,dex,con,int,wis,cha]
        self.name = name
        self.HP = HP
        self.maxHP = HP
        self.HD = HD
        self.initiative = init
        self.AC = AC
        self.abilities = abilities

    def alterHP(self, amount):
        self.HP += amount
        #constrain the HP to within bounds
        self.HP = self.HP if self.HP <= self.maxHP else self.maxHP
        self.HP = self.HP if self.HP >= 0 else 0


class character:
    def __init__(self, name, init):
        self.name = name
        self.initiative = r.call(init)


class charbuild:
    def __init__(self, master):
        self.win = tk.Toplevel()
        self.master = master

        self.name = util.labeledEntry(self.win, "Character Name", 0, 0)
        self.initiative = util.labeledEntry(self.win, "Initiative Score", 2, 0)

        self.finish = tk.Button(self.win,
                                text="Finish",
                                command=lambda: self.end())
        self.finish.grid(row=4, column=0)

    def end(self):
        self.master.placeCharacter(self)
        self.win.destroy()


class charsub:
    def __init__(self, master, character):
        self.f = tk.Frame(master)
        self.creature = character
        self.name = tk.Label(self.f, text=character.name, font="Calibri 18")
        self.name.pack()
        self.init = tk.Label(self.f,
                             text=character.initiative,
                             font="Calibri 14")
        self.init.pack()

    def refresh(self):
        pass

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


class sub:
    def __init__(self, master, monster):
        self.creature = monster

        self.f = tk.Frame(master, pady=10, bd=2, relief="groove")

        notattack = tk.Frame(self.f)
        notattack.grid(row=0, column=0)

        #############################

        namesec = tk.Frame(notattack)
        namesec.grid(row=0, column=0)
        self.nameL = tk.Label(namesec, text=monster.name, font="Calibri 18")
        self.nameL.grid(row=0, column=0, sticky='w')
        xpL = tk.Label(namesec, text='Initiative:  ' + str(monster.initiative))
        xpL.grid(row=0, column=1, sticky='e')

        ##############################

        hpsec = tk.Frame(notattack)
        hpsec.grid(row=1, column=1)

        hpLsec = tk.Frame(notattack)
        hpLsec.grid(row=0, column=1)

        self.hpL = tk.Label(hpLsec,
                            text='HP:  ' + str(monster.HP),
                            font='Calibri 18')
        self.hpL.grid(row=0, column=0, sticky='w')
        self.acL = tk.Label(hpLsec,
                            text='   AC:  ' + monster.AC,
                            font='Calibri 16')
        self.acL.grid(row=0, column=1, sticky='e')

        hpmain = tk.Frame(hpsec)
        hpmain.grid(row=1, column=0)

        self.change = util.labeledEntry(hpmain, 'Change in HP', 0, 0)

        hpdo = tk.Button(hpmain,
                         text='Change',
                         command=lambda: self.changeHP())
        hpdo.grid(row=1, column=1)

        #################################

        attacksec = tk.Frame(self.f)
        attacksec.grid(row=1, column=0)
        attacknotresult = tk.Frame(attacksec)
        attacknotresult.grid(row=0, column=0)

        self.attackE = util.labeledEntry(attacknotresult,
                                         'Attack Modifiers',
                                         0,
                                         0,
                                         orient='h',
                                         pos='w',
                                         width=15)

        self.damageE = util.labeledEntry(attacknotresult,
                                         'Damage',
                                         1,
                                         0,
                                         orient='h',
                                         pos='w',
                                         width=15)

        perform = tk.Button(attacknotresult,
                            text="Attack",
                            command=lambda: self.doattack())
        perform.grid(row=1, column=2)

        advsec = tk.Frame(attacknotresult)
        advsec.grid(row=0, column=2)

        self.advantage = tk.BooleanVar()
        self.disadvantage = tk.BooleanVar()
        hasAdvantage = tk.Checkbutton(advsec,
                                      text="Advantage?",
                                      variable=self.advantage)
        hasAdvantage.grid(row=0, column=1, sticky="w")
        hasDisadvantage = tk.Checkbutton(advsec,
                                         text="Disadvantage?",
                                         variable=self.disadvantage)
        hasDisadvantage.grid(row=1, column=1, sticky="w")

        self.attackresult = tk.Label(attacksec)
        self.attackresult.grid(row=1, column=0)
        self.damageresult = tk.Label(attacksec)
        self.damageresult.grid(row=2, column=0)

        ############################################

        abilframe = tk.Frame(notattack)
        abilframe.grid(row=1, column=0)

        abilnames = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        for i in range(len(abilnames)):
            tk.Label(abilframe,
                     text=abilnames[i]).grid(row=(i // 3) * 2,
                                             column=i % 3)
            tk.Label(abilframe,
                     text=str(self.creature.abilities[i]) + " (" + str(
                         modifier(self.creature.abilities[i])) + ")").grid(
                             row=(i // 3) * 2 + 1,
                             column=i % 3)

    def doattack(self):
        if (self.advantage.get() and not self.disadvantage.get()):
            attstring = '2d20h1'
        elif (not self.advantage.get() and self.disadvantage.get()):
            attstring = '2d20l1'
        else:
            attstring = '1d20'
        attroll = r.call(attstring)

        if (self.attackE.get()):
            attmodifiers = r.call(self.attackE.get())
        else:
            attmodifiers = 0

        if (attroll == 20):
            attresult = 'Critical Hit'
            damresult = str(r.call(self.damageE.get(), option='critical'))
        elif (attroll == 1):
            attresult = 'Critical Miss'
            damresult = '0'
        else:
            attresult = str(attroll + attmodifiers)
            damresult = str(r.call(self.damageE.get()))
        self.attackresult['text'] = 'Attack result: ' + attresult
        self.damageresult['text'] = 'Damage done: ' + damresult

    def changeHP(self):
        var = round(r.call(self.change.get()))
        self.creature.alterHP(var)
        self.refresh()

    def refresh(self):
        self.hpL['text'] = "HP:  " + str(self.creature.HP)
        if (self.creature.HP <= 0):
            every = all_children(self.f)
            every.append(self.f)
            for w in every:
                w['bg'] = 'red'

    def grid(self, r, c):
        self.f.grid(row=r, column=c)


class builder:
    #this will create a popup window that allows you to create new monsters and
    #add them to the main window
    def __init__(self, master):
        self.master = master
        self.win = tk.Toplevel()

        self.name = util.labeledEntry(self.win, 'Enter name', 0, 0)

        self.ac = util.labeledEntry(self.win, 'Enter AC', 2, 0)

        self.hp = util.labeledEntry(self.win, 'Enter HP as valid roll', 4, 0)

        self.av = tk.BooleanVar()
        self.average = tk.Checkbutton(self.win,
                                      text="Take average?",
                                      variable=self.av)
        self.average.grid(row=5, column=1)

        self.abil = tk.Frame(self.win)
        self.abil.grid(row=6, column=0)
        abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        self.entries = []
        labels = []
        for (i, n) in enumerate(abilities):
            self.entries.append(util.labeledEntry(self.abil,
                                                  n,
                                                  (i // 3) * 2,
                                                  i % 3,
                                                  width=4))

        self.resolve = tk.Button(self.win,
                                 text='Finish',
                                 command=lambda: self.finish(self.master))
        self.resolve.grid(row=9, column=0)

        self.copy()

    def copy(self):
        if (len(self.master.frames)):
            prev = self.master.frames[-1].creature
            if (type(prev) is monster):
                util.replaceEntry(self.name, prev.name)
                util.replaceEntry(self.ac, prev.AC)
                util.replaceEntry(self.hp, prev.HD)
                #replaceEntry(self.xp,prev.XP)
                for i in range(6):
                    util.replaceEntry(self.entries[i], prev.abilities[i])

    def finish(self, master):
        #tell main to take data out
        master.pull(self)
        #and end
        self.win.destroy()


class main:
    #this will handle the main window and have all the individual monsters'
    #frames packed in
    def __init__(self, window):
        self.master = window
        self.master.minsize(width=150, height=50)
        self.frames = []
        self.buttons = tk.Frame(window)
        self.makenew = tk.Button(self.buttons,
                                 text='New Monster',
                                 command=lambda: self.create())
        self.makenew.grid(row=0, column=0)
        self.makechar = tk.Button(self.buttons,
                                  text='New Character',
                                  command=lambda: charbuild(self))
        self.makechar.grid(row=0, column=1)
        self.qa = tk.Button(self.buttons,
                            text='Quit',
                            command=lambda: self.end())
        self.qa.grid(row=0, column=2)
        self.generalRoll = rollsec(window, self)
        self.draw()

    def draw(self):
        self.frames.sort(key=lambda obj: obj.creature.initiative, reverse=True)
        for (i, f) in enumerate(self.frames):
            f.refresh()
            f.grid(i % 3, i // 3)
        self.buttons.grid(row=3,
                          column=abs(len(self.frames) - 1) // 6,
                          sticky='n')
        self.generalRoll.grid(len(self.frames) % 3, len(self.frames) // 3)

    def create(self):
        new = builder(self)

        #otherwin is an object of class builder
    def pull(self, otherwin):
        abils = [0, 0, 0, 0, 0, 0]
        for i in range(len(otherwin.entries)):
            abils[i] = int(otherwin.entries[i].get())
        hp = r.call(otherwin.hp.get(),
                    option='average') if otherwin.av.get() else r.call(
                        otherwin.hp.get())
        rv = monster(otherwin.name.get(),
                     hp,
                     otherwin.hp.get(),
                     r.call('1d20',
                            modifiers=modifier(abils[1])),
                     otherwin.ac.get(),
                     abils)
        self.frames.append(sub(self.master, rv))
        self.draw()

    def placeCharacter(self, otherwin):
        rv = character(otherwin.name.get(), otherwin.initiative.get())
        self.frames.append(charsub(self.master, rv))
        self.draw()

    def end(self):
        self.master.destroy()

#window = tk.Tk()
#app = main(window)
#window.mainloop()
