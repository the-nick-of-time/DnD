import tkinter as tk
import libraries.Monster

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

    def monstermanage(self):

    def characterplay(self):

    def charactercreate(self):
