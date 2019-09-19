#! /usr/bin/env python3

import os
import tkinter as tk

import dndice as d

import lib.classes as c
import lib.components as gui
import lib.helpers as h
import lib.interface as iface


class Definer:
    def __init__(self, window, callbackfun):
        pass


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
    def __init__(self, container, character, **kwargs):
        gui.Section.__init__(self, container, **kwargs)
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
        self.basicAttack = tk.Button(self.remainingf, text='User-Defined\nAttack and Damage', command=lambda: self.attack(None))
        self.output = AttackDisplay(self.f)
        self.draw_static()

    def draw_static(self):
        self.buttonf.grid(row=0, column=0)
        s = 3
        for (i, obj) in enumerate(self.buttons):
            obj.grid(row=i//s, column=i%s)
        self.remainingf.grid(row=1, column=0)
        self.atkL.grid(row=0, column=0)
        self.atkbonus.grid(row=0, column=1)
        self.advbutton.grid(row=0, column=2)
        self.damL.grid(row=1, column=0)
        self.dambonus.grid(row=1, column=1)
        self.disbutton.grid(row=1, column=2)
        self.basicAttack.grid(row=2, column=1)
        ######
        self.output.grid(row=2, column=0)

    def attack(self, which):
        advantage = self.adv.get()
        disadvantage = self.dis.get()
        attack_bonus = self.character.parse_vars(self.atkbonus.get(), False)
        damage_bonus = self.character.parse_vars(self.dambonus.get(), False)
        if (which is None):
            attack = h.d20_roll(advantage, disadvantage, self.character.bonuses.get('lucky', False))
            attack += d.compile(attack_bonus)
            attackRoll = attack.evaluate()
            if (attack.is_critical()):
                mode = d.Mode.CRIT
                attackRoll = 'Critical Hit!'
            elif (attack.is_fail()):
                attackRoll = 'Critical Miss.'
                # Make it return 0
            else:
                # mode = 'execute'
                mode = d.Mode.NORMAL
                attackRoll = attack.verbose_result()
            damageRoll = d.basic(damage_bonus, mode=mode)
            result = ('Attack Roll: ' + str(attackRoll), 'Damage Roll: ' + str(damageRoll), '')
            # result = ('Attack Roll: ' + str(atk), 'Damage Roll: ' + str(dam), '')
        else:
            result = which.attack(self.character, advantage, disadvantage, attack_bonus, damage_bonus)
        self.output.update(*result)


class Module(Attacks):
    def __init__(self, container, character):
        Attacks.__init__(self, container, character, bd=2, relief='groove')


class Main(gui.Section):
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
        path = iface.JsonInterface.OBJECTSPATH / 'character' / (name + '.character')
        if path.exists():
            jf = iface.JsonInterface('character/' + name + '.character')
        else:
            raise FileNotFoundError
        self.character = c.Character(jf)
        self.core = Attacks(self.f, self.character)
        self.draw_static()
        self.container.deiconify()

    def writequit(self):
        self.character.write()
        self.container.destroy()


if __name__ == '__main__':
    from pathlib import Path

    iface.JsonInterface.OBJECTSPATH = Path(os.path.dirname(os.path.abspath(__file__)) + '/../objects/')
    win = tk.Tk(screenName='Attacks')
    app = Main(win)
    app.pack()
    win.mainloop()
