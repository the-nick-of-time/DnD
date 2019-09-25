import tkinter as tk
from collections import OrderedDict
from functools import partial

import lib.abilitiesLib as abil
import lib.characterLib as char
import lib.components as gui
import lib.interface as iface


class OwnedSkillsDisplay(gui.Section):
    def __init__(self, container, character: 'char.Character', **kwargs):
        super().__init__(container, **kwargs)
        self.advantage = gui.AdvantageChooser(self.f).grid(7, 0, columnspan=3)
        self.display = gui.RollDisplay(self.f).grid(8, 0, columnspan=3)
        self.owner = character
        skills = iface.JsonInterface('skill/SKILLS.skill')
        self.skillMap = skills.get('/')
        for skill in self.skillMap:
            self.skillMap[skill] = abil.AbilityName(self.skillMap[skill])
        self.buttons = OrderedDict(
            [(name, gui.ProficientButton(self.f, name, name in self.owner.skills,
                                         command=partial(self.roll_check, name),
                                         width=12))
             for name in sorted(self.skillMap)]
        )
        for i, obj in enumerate(self.buttons.values()):
            obj.grid(i // 3, i % 3)

    def roll_check(self, name):
        _, roll = self.owner.ability_check(self.skillMap[name], name,
                                           self.advantage.advantage,
                                           self.advantage.disadvantage)
        self.display.set(roll)


class Module(OwnedSkillsDisplay):
    def __init__(self, container, character: 'char.Character'):
        super().__init__(container, character)


class Main(gui.MainModule):
    def __init__(self, window: tk.Tk):
        def creator(character: 'char.Character'):
            return Module(window, character)

        super().__init__(window, creator)


if __name__ == '__main__':
    win = gui.MainWindow()
    app = Main(win)
    win.mainloop()
