import tkinter as tk

import tools.libraries.rolling as r
import tools.libraries.tkUtility as util


class rollsec:
    def __init__(self, master, app):
        self.parent = master
        self.f = tk.Frame(master)
        self.generalRoll = util.labeledEntry(self.f, 'Dice to roll?', 0, 0)
        self.generalRoll.bind("<Return>", lambda event: self.doRoll())
        self.button = tk.Button(self.f,
                                text="ROLL",
                                command=lambda: self.doRoll())
        self.button.grid(row=2, column=1)
        self.result = tk.Label(self.f)
        self.result.grid(row=2, column=0)

    def doRoll(self):
        self.result["text"] = r.roll(self.generalRoll.get())

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class main():
    def __init__(self, window):
        roll = rollsec(window, self)
        roll.grid(0, 0)


if (__name__ == '__main__'):
    win = tk.Tk()
    application = main(win)
    win.mainloop()
