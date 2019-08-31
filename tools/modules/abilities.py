#! /usr/bin/env python3

import os
import sys
import tkinter as tk

sys.path.insert(0,
                os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

from classes import Character
import helpers as h
import GUIbasics as gui
import interface as iface


class AbilityDisplay(gui.Section):
    abilnames = ['Strength', 'Dexterity', 'Constitution',
                 'Intelligence', 'Wisdom', 'Charisma']

    def __init__(self, master, character):
        gui.Section.__init__(self, master)
        self.person = character
        self.thisf = tk.Frame(self.f)
        self.subf = tk.Frame(self.thisf)
        #############
        self.abilchecks = [tk.Button(self.subf, text=a[:3].upper(),
                                     command=lambda x=a: self.roll_check(x),
                                     width=4)
                           for a in self.abilnames]
        self.abiltexts = [tk.StringVar() for a in self.abilnames]
        self.scores = [tk.Entry(self.subf, width=4,
                                textvariable=self.abiltexts[i])
                       for (i, a) in enumerate(self.abilnames)]
        self.mods = [tk.Label(self.subf, width=2) for a in self.abilnames]
        self.saves = [tk.Button(self.subf, text='SAVE', width=4,
                                command=lambda x=a: self.roll_save(x))
                      for a in self.abilnames]
        ######
        self.adv = tk.BooleanVar()
        self.advbutton = tk.Checkbutton(self.f, text='Advantage?',
                                        variable=self.adv)
        self.dis = tk.BooleanVar()
        self.disbutton = tk.Checkbutton(self.f, text='Disadvantage?',
                                        variable=self.dis)
        self.rolldisplay = tk.Label(self.f)
        ######
        self.skills = SkillDisplay(self.thisf, self.person, self.rolldisplay,
                                   self.adv, self.dis)
        ######
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        self.thisf.grid(row=0, column=0)
        self.skills.grid(row=0, column=1)
        self.subf.grid(row=0, column=0)
        for (i, a) in enumerate(self.abilnames):
            self.abilchecks[i].grid(row=i, column=0)
            # util.replaceEntry(self.scores[i], self.person.abilities[a])
            self.abiltexts[i].set(self.person.abilities[a])
            self.scores[i].grid(row=i, column=1)
            self.mods[i].grid(row=i, column=2)
            self.saves[i].grid(row=i, column=3)
            if (a in self.person.saves):
                self.saves[i].config(bg='green', fg='white')
            self.abiltexts[i].trace('w',
                                    lambda a, b, c: self.update_character())
        self.advbutton.grid(row=1, column=0)
        self.disbutton.grid(row=2, column=0)
        self.rolldisplay.grid(row=3, column=0)

    def draw_dynamic(self):
        for (i, a) in enumerate(self.abilnames):
            self.mods[i]['text'] = h.modifier(self.scores[i].get() or 0)

    def roll_check(self, abil):
        advantage = self.adv.get()
        disadvantage = self.dis.get()
        result = self.person.ability_check(abil, adv=advantage,
                                           dis=disadvantage)
        self.rolldisplay['text'] = '{}+{}={}'.format(*reversed(result))

    def roll_save(self, abil):
        advantage = self.adv.get()
        disadvantage = self.dis.get()
        result = self.person.ability_save(abil, adv=advantage,
                                          dis=disadvantage)
        self.rolldisplay['text'] = '{}+{}={}'.format(*reversed(result))

    def update_character(self):
        for (i, a) in enumerate(self.abilnames):
            self.person.abilities[a] = int(self.scores[i].get() or 0)
        self.draw_dynamic()


class SkillDisplay(gui.Section):
    def __init__(self, container, character, output, adv, dis):
        gui.Section.__init__(self, container)
        self.person = character
        self.display = output
        self.adv = adv
        self.dis = dis
        sk = iface.JSONInterface('skill/SKILLS.skill')
        self.skillmap = sk.get('/')
        self.buttons = [tk.Button(self.f, text=n,
                                  command=lambda x=n: self.roll_check(x))
                        for n in sorted(self.skillmap)]
        self.draw_static()

    def draw_static(self):
        for (i, obj) in enumerate(self.buttons):
            obj.grid(row=i // 3, column=i % 3)
            if (obj['text'] in self.person.skills):
                obj.config(bg='green', fg='white')

    def roll_check(self, name):
        abil = self.skillmap[name]
        # mod = h.modifier(self.person.)
        advantage = self.adv.get()
        disadvantage = self.dis.get()
        result = self.person.ability_check(abil, skill=name, adv=advantage,
                                           dis=disadvantage)
        self.display['text'] = '{}+{}={}'.format(*reversed(result))


class module(AbilityDisplay):
    def __init__(self, container, character):
        AbilityDisplay.__init__(self, container, character)
        self.f.config(pady=5)


class main(gui.Section):
    def __init__(self, window):
        gui.Section.__init__(self, window)
        self.charactername = {}
        self.QUIT = tk.Button(self.f, text='QUIT', command=self.quit)
        self.startup_begin()

    def startup_begin(self):
        gui.Query(self.charactername, self.startup_end, 'Character Name?')
        self.container.withdraw()

    def startup_end(self):
        name = self.charactername['Character Name?']
        path = (iface.JSONInterface.OBJECTSPATH
                + 'character/' + name + '.character')
        if (os.path.exists(path)):
            jf = iface.JSONInterface('character/' + name + '.character')
        else:
            raise FileNotFoundError
        character = Character(jf)
        self.block = AbilityDisplay(self.f, character)
        self.draw_static()
        self.container.deiconify()

    def draw_static(self):
        self.block.grid(row=0, column=0)
        self.QUIT.grid(row=1, column=0)

    def quit(self):
        self.block.person.write()
        self.container.destroy()


if __name__ == '__main__':
    win = gui.MainWindow()
    iface.JSONInterface.OBJECTSPATH = os.path.dirname(os.path.abspath(__file__)) + '/../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
