#!/usr/bin/env python3

import tkinter as tk
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import tools.modules.character_manager as cm
import tools.modules.monsters as mm
import tools.modules.dice as dc
import tools.modules.character_creator as cc


class main:
    def __init__(self, window):
        self.window = window
        self.f = tk.Frame(window)
        self.playerframe = tk.LabelFrame(self.f, text='Player', padx=10,
                                         pady=5)
        self.dmframe = tk.LabelFrame(self.f, text='DM', padx=10, pady=5)
        self.rollframe = tk.LabelFrame(self.f, text='Any', padx=10, pady=5)
        self.charmanage = tk.Button(self.playerframe, text='Manage\nCharacter',
                                    command=self.charactermanager)
        self.charcreate = tk.Button(self.playerframe, text='Create\nCharacter',
                                    command=self.character_create)
        self.monstermanage = tk.Button(self.dmframe, text='Manage\nEncounter',
                                       command=self.monstermanager)
        self.diceroll = tk.Button(self.rollframe, text='Roll\nDice',
                                  command=self.dice)
        self.draw_static()

    def draw_static(self):
        self.f.pack()
        self.playerframe.grid(row=0, column=0)
        self.charmanage.pack()
        self.charcreate.pack()
        self.dmframe.grid(row=0, column=1)
        self.monstermanage.pack()
        self.rollframe.grid(row=0, column=2)
        self.diceroll.pack()

    def charactermanager(self):
        self.f.destroy()
        cm.main(self.window)

    def character_create(self):
        self.f.destroy()
        cc.main(self.window).pack()

    def monstermanager(self):
        self.f.destroy()
        mm.main(self.window).pack()

    def dice(self):
        self.f.destroy()
        dc.DiceRoll(self.window).pack()


win = tk.Tk()
win.title('D&D')
app = main(win)
win.mainloop()
