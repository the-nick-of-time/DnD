import tkinter as tk
from collections import OrderedDict
from functools import partial

import lib.abilitiesLib as abil
import lib.characterLib as char
import lib.components as gui
import lib.interface as iface


class OwnedSkillsDisplay(gui.Section):
    def __init__(self, container, character: 'char.Character', adv: gui.AdvantageChooser,
                 display: gui.RollDisplay, **kwargs):
        super().__init__(container, **kwargs)
        self.advantage = adv
        self.display = display
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
    def __init__(self, container, character: 'char.Character', adv: gui.AdvantageChooser,
                 display: gui.RollDisplay):
        super().__init__(container, character, adv, display)


class Main(gui.MainModule):
    def __init__(self, window: tk.Tk):
        self.advantage = gui.AdvantageChooser(window)
        self.display = gui.RollDisplay(window)

        def creator(character: 'char.Character'):
            return Module(window, character, self.advantage, self.display)

        super().__init__(window, creator)

        self.advantage.grid(1, 0)
        self.display.grid(2, 0)


if __name__ == '__main__':
    win = gui.MainWindow()
    app = Main(win)
    win.mainloop()
