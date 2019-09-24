#! /usr/bin/env python3

import tkinter as tk

import dndice as d

import lib.components as gui


class DiceRoll(gui.Section):
    def __init__(self, master):
        gui.Section.__init__(self, master)
        self.generalRoll = gui.LabeledEntry(self.f, 'Dice to roll?')
        self.generalRoll.grid(0, 0)
        self.generalRoll.bind("<Return>", lambda event: self.do_roll())
        self.generalRoll.bind("<KP_Enter>", lambda event: self.do_roll())
        self.button = tk.Button(self.f, text="ROLL", command=self.do_roll)
        self.button.grid(row=1, column=1)
        self.result = gui.RollDisplay(self.f)
        self.result.grid(1, 0)

    def do_roll(self):
        self.result.set(d.compile(self.generalRoll.get()))


class Module(DiceRoll):
    def __init__(self, container, character):
        DiceRoll.__init__(self, container)
        self.character = character

    def do_roll(self):
        s = self.generalRoll.get()
        parsed = self.character.parse_vars(s, mathIt=False)
        self.result.set(d.compile(parsed))


if __name__ == '__main__':
    win = gui.MainWindow()
    win.title('Dice')
    app = DiceRoll(win)
    app.pack()
    win.mainloop()
