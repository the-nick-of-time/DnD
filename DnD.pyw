#!/usr/bin/env python

import tkinter as tk

import tools.modules.monstermanager as mm
import tools.modules.charactermanager as cm
import tools.modules.charactercreator as cc
import tools.modules.dice as dc
# import tools.modules.charactereditor as ce
import tools.forge.inventory as iv
import tools.forge.hp as hp


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
        # edit = tk.Button(self.master,
        #                  text="Edit an Existing Character",
        #                  command=lambda: self.characteredit())
        # edit.grid(row=3, column=0, pady=5)
        inventory = tk.Button(self.master, text="Manage Your Inventory",
                              command=lambda: self.characterinventory())
        inventory.grid(row=3, column=0, pady=5)
        hpmanage = tk.Button(self.master, text="Manage Your HP",
                             command=lambda: self.characterhp())
        hpmanage.grid(row=4, column=0, pady=5)
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
            # widget.grid_forget()
            widget.destroy()

    def monstermanage(self):
        self.undisplay()
        mm.main(self.master)

    def characterplay(self):
        self.undisplay()
        cm.main(self.master)

    def charactercreate(self):
        self.undisplay()
        cc.main(self.master)

    def characterinventory(self):
        self.undisplay()
        iv.main(self.master)

    def characterhp(self):
        self.undisplay()
        hp.main(self.master)

#    def characteredit(self):
#        self.undisplay()
#        ce.main(self.master)

    def dicesimulator(self):
        self.undisplay()
        dc.main(self.master)


win = tk.Tk()
app = core(win)
win.mainloop()
