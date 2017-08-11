import tkinter as tk

import rolling as r
import tkUtility as util
import GUIbasics as gui

class DiceRoll(gui.Section):
    def __init__(self, master):
        gui.Section.__init__(self, master)
        self.generalRoll = util.labeledEntry(self.f, 'Dice to roll?', 0, 0)
        self.generalRoll.bind("<Return>", lambda event: self.do_roll())
        self.button = tk.Button(self.f, text="ROLL", command=self.do_roll)
        self.button.grid(row=2, column=1)
        self.result = tk.Label(self.f)
        self.result.grid(row=2, column=0)

    def do_roll(self):
        self.result["text"] = r.roll(self.generalRoll.get(), option='multipass')


class module(DiceRoll):
    def __init__(self, container, character):
        DiceRoll.__init__(self, container)
        self.character = character

    def do_roll(self):
        s = self.generalRoll.get()
        parsed = self.character.parse_vars(s, mathIt=False)
        self.result["text"] = r.roll(parsed, option='multipass')


if __name__ == '__main__':
    win = tk.Tk()
    app = DiceRoll(win)
    app.pack()
    win.mainloop()
