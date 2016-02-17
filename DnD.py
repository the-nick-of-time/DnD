import tkinter as tk

import libraries.monstermanager as mm
import libraries.charactermanager as cm
import libraries.charactercreator as cc

class core:
    def __init__(window):
        self.master = window
        playerframe = tk.Frame()
        DMframe = tk.Frame()
        playerlabel = tk.Label(playerframe, text = "Player")
        playerlabel.grid(row = 0, column = 0)
        DMlabel = tk.Label(DMframe, text = "DM")
        manage = tk.Button(playerframe, text = "Play a character", 
                command = lambda: self.characterplay())
        manage.grid(row = 1, column = 0)
        create = tk.Button(playerframe, text = "Create a new character", 
                command = lambda: self.charactercreate())
        create.grid(row = 2, column = 0)
        monster = tk.Button(DMframe, text = "Create new encounter", 
                command = lambda:self.monstermanage())
        monster.grid(row = 1, column = 0)

    def undisplay(self):
        for widget in self.master.winfo_children:
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

win = tk.Tk()
app = core(win)
win.mainloop()
