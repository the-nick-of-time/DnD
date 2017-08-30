#! /usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import GUIbasics as gui
import classes as c
import interface as iface
import helpers as h

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abilities
import dice
import hp
import inventory
import spells
import features
import resources
import attacks
import conditions
import equipment


class main:
    def __init__(self, window):
        self.container = window
        self.buttons = tk.Frame(window)
        self.QUIT = tk.Button(self.buttons, text='QUIT', fg='red',
                              command=self.writequit)
        self.long_rest = tk.Button(self.buttons, text='Long rest',
                                   command=lambda: self.rest('long'))
        self.short_rest = tk.Button(self.buttons, text='Short rest',
                                    command=lambda: self.rest('short'))
        self.next_turn = tk.Button(self.buttons, text='Next turn',
                                   command=lambda: self.rest('turn'))
        self.core = ttk.Notebook(window)
        self.core.bind("<<NotebookTabChanged>>", self.tab_update)
        ######
        self.frontpage = tk.Frame(self.core)
        self.featurespage = tk.Frame(self.core)
        self.attackpage = tk.Frame(self.core)
        self.inventorypage = tk.Frame(self.core)
        self.spellspage = tk.Frame(self.core)
        # self.draw_static()
        self.startup_begin()

    def draw_static(self):
        self.core.grid(row=0, column=0)
        ######
        # Front page
        self.core.add(self.frontpage, text='Main')
        self.info.grid(row=0, column=0)
        self.HP.grid(row=0, column=1)
        self.roller.grid(row=1, column=0)
        self.abils.grid(row=1, column=1)
        ######
        # Attacks
        self.core.add(self.attackpage, text='Attacks')
        self.attacktop.grid(row=0, column=0)
        self.attacks.grid(row=0, column=0, sticky='n')
        self.conditions.grid(row=0, column=1, sticky='n')
        self.equipment.grid(row=1, column=0)
        ######
        # Features
        self.core.add(self.featurespage, text='Features')
        self.features.grid(row=0, column=0)
        self.resources.grid(row=0, column=1)
        self.featureroller.grid(row=1, column=1)
        ######
        # Inventory
        self.core.add(self.inventorypage, text='Inventory')
        self.inventory.grid(row=0, column=0)
        ######
        # Spells
        self.core.add(self.spellspage, text='Spells')
        self.spells.grid(row=0, column=0)
        #####
        self.buttons.grid(row=1, column=0)
        self.next_turn.grid(row=0, column=0)
        self.short_rest.grid(row=0, column=1)
        self.long_rest.grid(row=0, column=2)
        self.QUIT.grid(row=0, column=3)

    def startup_begin(self):
        self.charactername = {}
        gui.Query(self.charactername, self.startup_end, 'Character Name?')
        self.container.withdraw()

    def startup_end(self):
        name = self.charactername['Character Name?']
        path = 'character/' + h.clean(name) + '.character'
        if (os.path.exists(iface.JSONInterface.OBJECTSPATH + path)):
            self.record = iface.JSONInterface(path)
        else:
            gui.ErrorMessage('A character with that name was not found.')
            print(iface.JSONInterface.OBJECTSPATH + path)
            raise FileNotFoundError
        self.character = c.Character(self.record)
        self.container.title(str(self.character))
        self.settingmenu = Settings(self.container, self.character)
        self.container.config(menu=self.settingmenu.core)
        ######
        # Front page
        self.info = Information(self.frontpage, self.character)
        self.HP = hp.module(self.frontpage, self.character)
        self.roller = dice.module(self.frontpage, self.character)
        self.abils = abilities.module(self.frontpage, self.character)
        ######
        # Attacks
        self.attacktop = tk.Frame(self.attackpage)
        self.attacks = attacks.module(self.attacktop, self.character)
        self.conditions = conditions.module(self.attacktop, self.character)
        self.equipment = equipment.module(self.attackpage, self.character)
        ######
        # Features
        self.features = features.module(self.featurespage, self.character)
        self.resources = resources.module(self.featurespage, self.character)
        self.featureroller = dice.module(self.featurespage, self.character)
        ######
        # Inventory
        self.inventory = inventory.module(self.inventorypage, self.character)
        ######
        # Spells
        self.spells = spells.module(self.spellspage, self.character)
        ######
        self.container.deiconify()
        self.draw_static()

    def writequit(self):
        self.character.write()
        self.container.destroy()

    def rest(self, which):
        self.character.rest(which)
        self.spells.draw_dynamic()
        self.resources.draw_dynamic()
        self.HP.draw_dynamic()
        self.conditions.draw_dynamic()

    def tab_update(self, event):
        index = event.widget.index('current')
        if (index == 0):
            self.info.draw_dynamic()
            self.HP.draw_dynamic()
        elif (index == 1):
            self.conditions.draw_dynamic()
        elif (index == 2):
            self.resources.draw_dynamic()
        elif (index == 3):
            self.inventory.draw_dynamic()
        elif (index == 4):
            self.spells.draw_dynamic()


class Information(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container)
        self.character = character
        self.name = tk.Label(self.f, text=str(character), font='Calibri 18')
        self.levels = tk.Label(self.f, text=str(character.classes))
        self.race = tk.Label(self.f, text=str(character.race))
        self.AC = tk.Label(self.f, text='AC: ' + str(character.AC))
        # self.speed = tk.Label(self.f, text=)
        # l = self.character.record.get('/languages')
        self.languages = tk.Label(self.f, text=', '.join(character.languages))
        self.draw_static()

    def draw_static(self):
        self.name.grid(row=0, column=0)
        self.levels.grid(row=1, column=0)
        self.race.grid(row=2, column=0)
        self.languages.grid(row=3, column=0)
        self.AC.grid(row=4, column=0)

    def draw_dynamic(self):
        self.AC.config(text='AC: ' + str(self.character.AC))


class Settings:
    def __init__(self, window, character):
        self.character = character
        if (not self.character.get('/SETTINGS')):
            self.character.set('/SETTINGS', {})
        self.core = tk.Menu(window)
        self.healingchoice = tk.Menu(self.core, tearoff=False)
        self.healing = tk.StringVar()
        self.healing.set(self.character.get('/SETTINGS/HEALING') or 'vanilla')
        self.healingchoice.add_radiobutton(label='Vanilla',
                                           variable=self.healing,
                                           command=self.set_healing,
                                           value='vanilla')
        self.healingchoice.add_radiobutton(label='Slow (DMG 267)',
                                           variable=self.healing,
                                           command=self.set_healing,
                                           value='slow')
        self.healingchoice.add_radiobutton(label='Healing Surge (DMG 266)',
                                           variable=self.healing,
                                           command=self.set_healing,
                                           value='fast')
        self.core.add_cascade(label='Healing', menu=self.healingchoice)
        self.profdice = tk.BooleanVar()
        self.profdice.set(self.character.get('/SETTINGS/PROFICIENCY_DICE')
                          or False)
        self.profdicechoice = tk.Menu(self.core, tearoff=False)
        self.profdicechoice.add_checkbutton(label='Use proficiency dice? '
                                            '(DMG 263)',
                                            variable=self.profdice,
                                            command=self.set_prof)
        self.core.add_cascade(label='Proficiency Dice',
                              menu=self.profdicechoice)

    def set_healing(self):
        c.Character.HEALING = self.healing.get()
        self.character.set('/SETTINGS/HEALING', c.Character.HEALING)

    def set_prof(self):
        c.Character.PROFICIENCY_DICE = self.profdice.get()
        self.character.set('/SETTINGS/PROFICIENCY_DICE',
                           c.Character.PROFICIENCY_DICE)


if (__name__ == '__main__'):
    win = tk.Tk()
    # win.wm_title('Character Manager')
    iface.JSONInterface.OBJECTSPATH = '../objects/'
    app = main(win)
    win.mainloop()
