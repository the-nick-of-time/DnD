#!/usr/bin/env python3

import tkinter as tk
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import tools.modules.character_manager as cm
import tools.modules.monsters as mm
import tools.modules.dice as dc
import tools.modules.character_creator as cc
import tools.modules.levelup as lu
import tools.modules.item_creator as ic


class main:
    def __init__(self, window):
        self.window = window
        self.f = tk.Frame(window)
        self.playerframe = tk.LabelFrame(self.f, text='Player', padx=10)
        self.dmframe = tk.LabelFrame(self.f, text='DM', padx=10)
        self.rollframe = tk.LabelFrame(self.f, text='Any', padx=10)
        self.charmanage = tk.Button(self.playerframe, text='Manage\nCharacter',
                                    command=self.charactermanager)
        self.charcreate = tk.Button(self.playerframe, text='Create\nCharacter',
                                    command=self.character_create)
        self.levelup = tk.Button(self.playerframe, text='Level up\nCharacter',
                                 command=self.character_levelup)
        self.monstermanage = tk.Button(self.dmframe, text='Manage\nEncounter',
                                       command=self.monstermanager)
        self.diceroll = tk.Button(self.rollframe, text='Roll\nDice',
                                  command=self.dice)
        self.itemcreator = tk.Button(self.rollframe, text='Create\nItem',
                                     command=self.create_item)
        self.draw_static()

    def draw_static(self):
        self.f.pack()
        self.playerframe.grid(row=0, column=0)
        self.charmanage.pack(pady=5)
        self.charcreate.pack(pady=5)
        self.levelup.pack(pady=5)
        self.dmframe.grid(row=0, column=1)
        self.monstermanage.pack(pady=5)
        self.rollframe.grid(row=0, column=2)
        self.diceroll.pack(pady=5)
        self.itemcreator.pack(pady=5)

    def charactermanager(self):
        self.f.destroy()
        cm.main(self.window)

    def character_create(self):
        self.f.destroy()
        cc.main(self.window).pack()

    def character_levelup(self):
        self.f.destroy()
        lu.main(self.window).pack()

    def monstermanager(self):
        self.f.destroy()
        mm.main(self.window).pack()

    def dice(self):
        self.f.destroy()
        dc.DiceRoll(self.window).pack()

    def create_item(self):
        self.f.destroy()
        ic.main(self.window).pack()


win = tk.Tk()
win.title('D&D')
app = main(win)
win.mainloop()
