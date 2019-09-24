import enum
import tkinter as tk

import dndice as d

import lib.abilitiesLib as abil
import lib.characterLib as char
import lib.components as gui


class DisplayMode(enum.Enum):
    """How the abilities should be displayed, in ROW x COLUMN order."""
    SIX_BY_ONE = '6x1'
    THREE_BY_TWO = '3x2'
    TWO_BY_THREE = '2x3'
    ONE_BY_SIX = '1X6'


class AbilityDisplay(gui.Section):
    def __init__(self, parent, ability: 'abil.Ability', mode: DisplayMode,
                 advantage: gui.AdvantageChooser, display: gui.RollDisplay, **kwargs):
        super().__init__(parent, **kwargs)
        self.ability = ability
        self.advantage = advantage
        self.display = display
        self.check = tk.Button(self.f, width=4, text=ability.abbreviation,
                               command=self.roll_check)
        self.score = gui.NumericEntry(self.f, width=4)
        self.modifier = tk.Label(self.f, width=2)
        self.save = tk.Button(self.f, width=4, text='SAVE',
                              command=self.roll_save)
        self.check.grid(row=0, column=0)
        if mode == DisplayMode.SIX_BY_ONE:
            self.score.grid(row=0, column=1)
            self.modifier.grid(row=0, column=2)
            self.save.grid(row=0, column=3)
        else:
            self.score.grid(row=1, column=0)
            self.modifier.grid(row=2, column=0)
            self.save.grid(row=3, column=0)
        self.update_view()

    def update_view(self):
        self.score.set(self.ability.score)
        self.modifier['text'] = '{:+d}'.format(self.ability.modifier)

    def roll_check(self):
        expr = self.advantage.d20_roll()
        expr += d.compile(self.ability.modifier)
        self.display.set(expr)

    def roll_save(self):
        self.roll_check()


class StaticAbilityDisplay(gui.Section):
    def __init__(self, container, ability: 'abil.Ability', mode: DisplayMode):
        super().__init__(container)
        self.ability = ability
        self.name = tk.Label(self.f, text=self.ability.abbreviation)
        self.name.grid(row=0, column=0)
        numbers = '{s} ({m})'.format(s=ability.score, m=ability.modifier)
        self.numbers = tk.Label(self.f, text=numbers)
        if mode == DisplayMode.SIX_BY_ONE:
            self.numbers.grid(row=0, column=1)
        else:
            self.numbers.grid(row=1, column=0)


class AbilitiesDisplay(gui.Section):
    def __init__(self, container, abilities: 'abil.Abilities', mode: DisplayMode, static=False, **kwargs):
        super().__init__(container, **kwargs)
        self.abilities = abilities
        self.advantage = gui.AdvantageChooser(self.f)
        self.rollDisplay = gui.RollDisplay(self.f)
        if static:
            self.displays = [StaticAbilityDisplay(self.f, self.abilities[name], mode)
                             for name in abil.AbilityName]
        else:
            self.displays = [AbilityDisplay(self.f, self.abilities[name], mode,
                                            self.advantage, self.rollDisplay)
                             for name in abil.AbilityName]

        def calculate_pos(index):
            if mode == DisplayMode.SIX_BY_ONE:
                return index, 0
            if mode == DisplayMode.TWO_BY_THREE:
                # Row 1: STR DEX CON   Row 2: INT WIS CHA
                return index // 3, index % 3
            if mode == DisplayMode.THREE_BY_TWO:
                # Column 1: STR DEX CON   Column 2: INT WIS CHA
                return index % 3, index // 3
            if mode == DisplayMode.ONE_BY_SIX:
                return 0, index
            raise TypeError('Mode argument is incorrect')

        for i, display in enumerate(self.displays):
            display.grid(*calculate_pos(i))

        self.advantage.grid(6, 0)
        self.rollDisplay.grid(7, 0)

    def update_view(self):
        for display in self.displays:
            display.update_view()


class Module(AbilitiesDisplay):
    def __init__(self, container, character: 'char.Character'):
        self.owner = character
        super().__init__(container, character.abilities, DisplayMode.SIX_BY_ONE, pady=5)


class Main(gui.MainModule):
    def __init__(self, window: tk.Tk):
        def creator(character: 'char.Character'):
            return Module(window, character)
        super().__init__(window, creator)


if __name__ == '__main__':
    win = gui.MainWindow()
    app = Main(win)
    win.mainloop()
