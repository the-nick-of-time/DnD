#! /usr/bin/env python3

import os
import tkinter as tk
import tkinter.ttk as ttk

import abilities
import attacks
import conditions
import dice
import equipment
import features
import hp
import inventory
import lib.classes as c
import lib.components as gui
import lib.helpers as h
import lib.interface as iface
import resources
import spells


class Main:
    def __init__(self, window):
        self.container = window
        self.buttons = tk.Frame(window)
        self.QUIT = tk.Button(self.buttons, text='QUIT', fg='red',
                              command=self.write_quit)
        self.long_rest = tk.Button(self.buttons, text='Long rest',
                                   command=lambda: self.rest('long'))
        self.short_rest = tk.Button(self.buttons, text='Short rest',
                                    command=lambda: self.rest('short'))
        self.next_turn = tk.Button(self.buttons, text='Next turn',
                                   command=lambda: self.rest('turn'))
        self.core = ttk.Notebook(window)
        self.core.bind("<<NotebookTabChanged>>", self.tab_update)
        ######
        self.frontPage = tk.Frame(self.core)
        self.featuresPage = tk.Frame(self.core)
        self.attackPage = tk.Frame(self.core)
        self.inventoryPage = tk.Frame(self.core)
        self.spellsPage = tk.Frame(self.core)
        # self.draw_static()
        self.startup_begin()

    def draw_static(self):
        self.core.grid(row=0, column=0)
        ######
        # Front page
        self.core.add(self.frontPage, text='Main')
        self.info.grid(row=0, column=0)
        self.HP.grid(row=0, column=1)
        self.roller.grid(row=1, column=0)
        self.abils.grid(row=1, column=1)
        ######
        # Attacks
        self.core.add(self.attackPage, text='Attacks')
        self.attackTop.grid(row=0, column=0)
        self.attacks.grid(row=0, column=0, sticky='n')
        self.conditions.grid(row=0, column=1, sticky='n')
        self.equipment.grid(row=1, column=0)
        ######
        # Features
        self.core.add(self.featuresPage, text='Features')
        self.features.grid(row=0, column=0)
        self.resources.grid(row=0, column=1)
        self.featureRoller.grid(row=1, column=1)
        ######
        # Inventory
        self.core.add(self.inventoryPage, text='Inventory')
        self.inventory.grid(row=0, column=0)
        ######
        # Spells
        self.core.add(self.spellsPage, text='Spells')
        self.spells.grid(row=0, column=0)
        #####
        self.buttons.grid(row=1, column=0)
        self.next_turn.grid(row=0, column=0)
        self.short_rest.grid(row=0, column=1)
        self.long_rest.grid(row=0, column=2)
        self.QUIT.grid(row=0, column=3)

    # noinspection PyAttributeOutsideInit
    def startup_begin(self):
        self.charactername = {}
        gui.CharacterQuery(self.charactername, self.startup_end)
        self.container.withdraw()

    # noinspection PyAttributeOutsideInit
    def startup_end(self):
        name = self.charactername['Character Name?']
        path = Path('character/') / h.clean(name) / '.character'
        if os.path.exists(iface.JsonInterface.OBJECTSPATH / path):
            self.record = iface.JsonInterface(path)
        else:
            gui.ErrorMessage('A character with that name was not found.')
            print(iface.JsonInterface.OBJECTSPATH / path)
            raise FileNotFoundError
        self.character = c.Character(self.record)
        self.container.title(str(self.character))
        self.settingMenu = Settings(self.container, self.character)
        self.container.config(menu=self.settingMenu.core)
        ######
        # Front page
        self.info = Information(self.frontPage, self.character)
        self.HP = hp.Module(self.frontPage, self.character)
        self.roller = dice.Module(self.frontPage, self.character)
        self.abils = abilities.Module(self.frontPage, self.character)
        ######
        # Attacks
        self.attackTop = tk.Frame(self.attackPage)
        self.attacks = attacks.Module(self.attackTop, self.character)
        self.conditions = conditions.Module(self.attackTop, self.character)
        self.equipment = equipment.Module(self.attackPage, self.character)
        ######
        # Features
        self.features = features.Module(self.featuresPage, self.character)
        self.resources = resources.Module(self.featuresPage, self.character)
        self.featureRoller = dice.Module(self.featuresPage, self.character)
        ######
        # Inventory
        self.inventory = inventory.Module(self.inventoryPage, self.character)
        ######
        # Spells
        self.spells = spells.Module(self.spellsPage, self.character)
        ######
        self.container.deiconify()
        self.draw_static()

    def write_quit(self):
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
        if index == 0:
            self.info.draw_dynamic()
            self.HP.draw_dynamic()
        elif index == 1:
            self.conditions.draw_dynamic()
        elif index == 2:
            self.resources.draw_dynamic()
        elif index == 3:
            self.inventory.draw_dynamic()
        elif index == 4:
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
        if not self.character.get('/SETTINGS'):
            self.character.set('/SETTINGS', {})
        self.core = tk.Menu(window)
        self.healingChoice = tk.Menu(self.core, tearoff=False)
        self.healing = tk.StringVar()
        self.healing.set(self.character.get('/SETTINGS/HEALING') or 'vanilla')
        self.healingChoice.add_radiobutton(label='Vanilla',
                                           variable=self.healing,
                                           command=self.set_healing,
                                           value='vanilla')
        self.healingChoice.add_radiobutton(label='Slow (DMG 267)',
                                           variable=self.healing,
                                           command=self.set_healing,
                                           value='slow')
        self.healingChoice.add_radiobutton(label='Healing Surge (DMG 266)',
                                           variable=self.healing,
                                           command=self.set_healing,
                                           value='fast')
        self.core.add_cascade(label='Healing', menu=self.healingChoice)
        self.profDice = tk.BooleanVar()
        self.profDice.set(self.character.get('/SETTINGS/PROFICIENCY_DICE')
                          or False)
        self.profDiceChoice = tk.Menu(self.core, tearoff=False)
        self.profDiceChoice.add_checkbutton(label='Use proficiency dice? '
                                            '(DMG 263)',
                                            variable=self.profDice,
                                            command=self.set_prof)
        self.core.add_cascade(label='Proficiency Dice',
                              menu=self.profDiceChoice)

    def set_healing(self):
        c.Character.HEALING = self.healing.get()
        self.character.set('/SETTINGS/HEALING', c.Character.HEALING)

    def set_prof(self):
        c.Character.PROFICIENCY_DICE = self.profDice.get()
        self.character.set('/SETTINGS/PROFICIENCY_DICE',
                           c.Character.PROFICIENCY_DICE)


if __name__ == '__main__':
    from pathlib import Path

    iface.JsonInterface.OBJECTSPATH = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / 'objects'
    win = gui.MainWindow()
    app = Main(win)
    win.mainloop()
