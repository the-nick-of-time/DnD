import enum
import tkinter as tk

import lib.abilitiesLib as abil
import lib.characterLib as char
import lib.components as gui


class DisplayMode(enum.Enum):
    """How the abilities should be displayed, in ROW x COLUMN order."""
    SIX_BY_ONE = '6x1'
    THREE_BY_TWO = '3x2'
    TWO_BY_THREE = '2x3'
    ONE_BY_SIX = '1X6'


class AbilityDisplay(gui.LabeledEntry):
    def __init__(self, parent, ability: 'abil.Ability', mode: DisplayMode):
        self.ability = ability
        if mode == DisplayMode.SIX_BY_ONE:
            orient = gui.Direction.HORIZONTAL
        else:
            orient = gui.Direction.VERTICAL
        super().__init__(parent, ability.abbreviation, orient=orient, width=4)
        # Consistent width for alignment
        self.label['width'] = 4
        self.modLabel = tk.Label(self.f, width=2)
        if orient == gui.Direction.VERTICAL:
            self.modLabel.grid(row=2, column=0)
        elif orient == gui.Direction.HORIZONTAL:
            self.modLabel.grid(row=0, column=2)
        # Check if the value is an int
        validate = (self.entry.register(self.try_update_score), '%P')
        self.entry['validate'] = 'key'
        self.entry['validatecommand'] = validate

        self.update_view()

    def try_update_score(self, score: str):
        try:
            self.ability.score = int(score)
            self.modLabel['text'] = str(self.ability.modifier)
            return True
        except ValueError:
            return False

    def update_view(self):
        self.replace_text(str(self.ability.score))
        self.modLabel['text'] = str(self.ability.modifier)


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
        if static:
            self.displays = [StaticAbilityDisplay(self.f, self.abilities[name], mode)
                             for name in abil.AbilityName]
        else:
            self.displays = [AbilityDisplay(self.f, self.abilities[name], mode)
                             for name in abil.AbilityName]

        def calculate_pos(index):
            if mode == DisplayMode.SIX_BY_ONE:
                return index, 0
            if mode == DisplayMode.TWO_BY_THREE:
                return index // 3, index % 3
            if mode == DisplayMode.THREE_BY_TWO:
                return index // 2, index % 2
            if mode == DisplayMode.ONE_BY_SIX:
                return 0, index
            raise TypeError('Mode argument is incorrect')

        for i, display in enumerate(self.displays):
            display.grid(*calculate_pos(i))

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
