import tkinter as tk

import GUIbasics as gui
import classes as c
import interface as iface

import abilities
import dice
import hp
import inventory
import spells


class main:
    def __init__(self, window):
        self.container = window
        self.core = tk.ttk.Notebook(window)
        ######
        self.frontpage = tk.Frame(self.core)
        self.inventorypage = tk.Frame(self.core)
        self.spellspage = tk.Frame(self.core)

    def startup_begin(self):
        self.charactername = {}
        gui.Query(self.charactername, self.startup_end, 'Character Name?')
        self.container.withdraw()

    def startup_end(self):
        # Front page
        ######
        # Inventory
        ######
        # Spells
        ######
        self.container.deiconify()
