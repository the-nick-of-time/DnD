import tkinter as tk

import libraries.monstermanager as mm
import libraries.charactermanager as cm
import libraries.charactercreator as cc
import libraries.dice as dc


class core:
    def __init__(self, window):
        self.master = window
        playerlabel = tk.Label(self.master, text="Player", font="Calibri 20")
        playerlabel.grid(row=0, column=0)
        DMlabel = tk.Label(self.master, text="DM", font="Calibri 20")
        DMlabel.grid(row=0, column=1)
        manage = tk.Button(self.master,
                           text="Play a Character",
                           command=lambda: self.characterplay())
        manage.grid(row=1, column=0)
        create = tk.Button(self.master,
                           text="Create a New Character",
                           command=lambda: self.charactercreate())
        create.grid(row=2, column=0, pady=5)
        monster = tk.Button(self.master,
                            text="Create New Encounter",
                            command=lambda: self.monstermanage())
        monster.grid(row=1, column=1, padx=10)
        dicelabel = tk.Label(self.master, text="Dice", font="Calibri 20")
        dicelabel.grid(row=0, column=2)
        dice = tk.Button(self.master,
                         text="Roll Dice",
                         command=lambda: self.dicesimulator())
        dice.grid(row=1, column=2)

    def undisplay(self):
        for widget in self.master.winfo_children():
            widget.grid_forget()

    def monstermanage(self):
        self.undisplay()
        mm.main(self.master)

    def characterplay(self):
        self.undisplay()
        cm.main(self.master)

    def charactercreate(self):
        self.undisplay()
        cc.main(self.master)

    def dicesimulator(self):
        self.undisplay()
        dc.main(self.master)


win = tk.Tk()
app = core(win)
win.mainloop()
