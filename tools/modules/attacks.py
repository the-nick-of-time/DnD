import tkinter as tk
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import classes as c
import GUIbasics as gui
import interface as iface
import helpers as h


class AttackDisplay(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.atk = tk.Label(self.f)
        self.dam = tk.Label(self.f)
        self.eff = gui.EffectPane(self.f, '', '')
        self.draw_static()

    def draw_static(self):
        self.atk.grid(row=0, column=0)
        self.dam.grid(row=1, column=0)
        self.eff.grid(row=2, column=0)

    def update(self, attack, damage, effect):
        self.atk.config(text=attack)
        self.dam.config(text=damage)
        self.eff.update(h.shorten(effect), effect)


class Attacks(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container)
        self.character = character
        self.buttonf = tk.Frame(self.f)
        attacknames = sorted(self.character.attacks)
        self.buttons = [tk.Button(self.buttonf, text=n, command=lambda x=self.character.attacks[n]: self.attack(x)) for n in attacknames]
        self.remainingf = tk.Frame(self.f)
        self.adv = tk.BooleanVar()
        self.advbutton = tk.Checkbutton(self.remainingf, text='Advantage?', variable=self.adv)
        self.dis = tk.BooleanVar()
        self.disbutton = tk.Checkbutton(self.remainingf, text='Disadvantage?', variable=self.dis)
        self.atkL = tk.Label(self.remainingf, text='Attack Bonus')
        self.atkbonus = tk.Entry(self.remainingf)
        self.damL = tk.Label(self.remainingf, text='Damage Bonus')
        self.dambonus = tk.Entry(self.remainingf)
        self.output = AttackDisplay(self.f)
        self.draw_static()

    def draw_static(self):
        self.buttonf.grid(row=0, column=0)
        s = 6
        for (i, obj) in enumerate(self.buttons):
            obj.grid(row=i%s, column=i//s)
        self.remainingf.grid(row=1, column=0)
        self.atkL.grid(row=0, column=0)
        self.atkbonus.grid(row=0, column=1)
        self.advbutton.grid(row=0, column=2)
        self.damL.grid(row=1, column=0)
        self.dambonus.grid(row=1, column=1)
        self.disbutton.grid(row=1, column=2)
        ######
        self.output.grid(row=2, column=0)

    def attack(self, which):
        advantage = self.adv.get()
        disadvantage = self.dis.get()
        attack_bonus = self.atkbonus.get()
        damage_bonus = self.dambonus.get()
        result = which.attack(self.character, advantage, disadvantage, attack_bonus, damage_bonus)
        self.output.update(*result)


class module(Attacks):
    def __init__(self, container, character):
        Attacks.__init__(self, container, character)


class main(gui.Section):
    def __init__(self, window):
        gui.Section.__init__(self, window)
        self.charactername = {}
        self.QUIT = tk.Button(self.f, text='QUIT', command=self.writequit)
        self.startup_begin()

    def draw_static(self):
        self.core.grid(row=0, column=0)
        self.QUIT.grid(row=1, column=1)

    def startup_begin(self):
        gui.Query(self.charactername, self.startup_end, 'Character Name?')
        self.container.withdraw()

    def startup_end(self):
        name = self.charactername['Character Name?']
        path = iface.JSONInterface.OBJECTSPATH + 'character/' + name + '.character'
        if (os.path.exists(path)):
            jf = iface.JSONInterface('character/' + name + '.character')
        else:
            raise FileNotFoundError
        character = c.Character(jf)
        self.core = Attacks(self.f, character)
        self.draw_static()
        self.container.deiconify()

    def writequit(self):
        self.character.write()
        self.container.destroy()


if (__name__ == '__main__'):
    win = tk.Tk(screenName='Attacks')
    iface.JSONInterface.OBJECTSPATH = '../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
