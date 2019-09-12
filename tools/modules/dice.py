#! /usr/bin/env python3

import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import dndice as d

import components as gui


class DiceRoll(gui.Section):
    def __init__(self, master):
        gui.Section.__init__(self, master)
        self.generalRoll = gui.LabeledEntry(self.f, 'Dice to roll?')
        self.generalRoll.grid(0, 0)
        self.generalRoll.bind("<Return>", lambda event: self.do_roll())
        self.button = tk.Button(self.f, text="ROLL", command=self.do_roll)
        self.button.grid(row=1, column=1)
        self.result = tk.Label(self.f)
        self.result.grid(row=1, column=0)

    def do_roll(self):
        self.result["text"] = d.verbose(self.generalRoll.get())


class Module(DiceRoll):
    def __init__(self, container, character):
        DiceRoll.__init__(self, container)
        self.character = character

    def do_roll(self):
        s = self.generalRoll.get()
        parsed = self.character.parse_vars(s, mathIt=False)
        self.result["text"] = d.verbose(parsed)


if __name__ == '__main__':
    win = gui.MainWindow()
    win.title('Dice')
    app = DiceRoll(win)
    app.pack()
    win.mainloop()
