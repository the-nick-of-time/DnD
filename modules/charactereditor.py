import os.path
import tkinter as tk
import configparser as cp

from ..libraries import rolling as r
from ..libraries import tkUtility as util


class main:
    def __init__(self, win):
        self.master = win

        self.popWin = tk.Toplevel()
        self.pop = popup(self, self.popWin)

        self.io = cp.ConfigParser()


class popup:
    def __init__(self, master, popWindow):
        self.win = popWindow
        self.master = master

        self.question = util.labeledEntry(self.win, "Enter character name\n"
                                          "as it appears in the file", 0, 0)
        self.accept = tk.Button(self.win, text="Accept",
                                command=lambda:self.verify())
        self.accept.grid(row=2, column=0)

    def verify(self):
        filename = "./character/" + self.question.get() + ".ini"
        if(os.path.isfile(filename)):
            self.master.io.read(filename)
            self.win.destroy()
        else:
            errorWindow = tk.Toplevel()
            tk.Label(
                errorWindow,
                text=
                "There is no .ini file in the character directory\nwith name "
                + self.question.get()).pack()
            tk.Button(errorWindow,
                      command=errorWindow.destroy,
                      text="OK").pack()
            
class spellsec:
