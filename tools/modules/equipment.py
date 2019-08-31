#! /usr/bin/env python3

import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import components as gui
import classes as c
import interface as iface


# TODO: Add held items with corresponding frames; somehow deal with versatile weapons
# TODO: only show apparel and weapons in buttons for the module

class EquipmentDisplay(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.registry = {}
        ######
        self.headF = tk.LabelFrame(self.f, text='Head', width=60, height=40)
        # self.headF.pack_propagate(0)
        self.head = tk.Label(self.headF)
        self.neckF = tk.LabelFrame(self.f, text='Neck', width=40, height=30)
        # self.neckF.pack_propagate(0)
        self.neck = tk.Label(self.neckF)
        self.lefthandF = tk.LabelFrame(self.f, text='Hands', width=40, height=40)
        # self.lefthandF.pack_propagate(0)
        self.lefthand = tk.Label(self.lefthandF)
        self.righthandF = tk.LabelFrame(self.f, text='Hands', width=40, height=40)
        # self.righthandF.pack_propagate(0)
        self.righthand = tk.Label(self.righthandF)
        self.clothesF = tk.LabelFrame(self.f, text='Clothes', width=120, height=120)
        # self.clothesF.pack_propagate(0)
        self.clothes = tk.Label(self.clothesF)
        self.cloakF = tk.LabelFrame(self.f, text='Cloak', width=80, height=120)
        # self.cloakF.pack_propagate(0)
        self.cloak = tk.Label(self.cloakF)
        self.beltF = tk.LabelFrame(self.f, text='Belt', width=120, height=40)
        # self.beltF.pack_propagate(0)
        self.belt = tk.Label(self.beltF)
        self.pantsF = tk.LabelFrame(self.f, text='Pants', width=80, height=120)
        # self.pantsF.pack_propagate(0)
        self.pants = tk.Label(self.pantsF)
        self.leftbootF = tk.LabelFrame(self.f, text='Boots', width=40, height=40)
        # self.leftbootF.pack_propagate(0)
        self.leftboot = tk.Label(self.leftbootF)
        self.rightbootF = tk.LabelFrame(self.f, text='Boots', width=40, height=40)
        # self.rightbootF.pack_propagate(0)
        self.rightboot = tk.Label(self.rightbootF)
        #####
        self.basecolor = self.headF.cget('bg')
        # self.buttons = tk.Frame(self.f)
        # self.do_equip = tk.Button(self.buttons, text='Equip', command=lambda: self.equip(slot='necklace', name='Amulet'))
        # self.un_equip = tk.Button(self.buttons, text='Unequip', command=lambda: self.unequip(name='Amulet'))
        self.draw_static()

    def draw_static(self):
        self.headF.grid(row=0, column=1)
        self.head.pack()
        self.neckF.grid(row=1, column=1)
        self.neck.pack()
        self.lefthandF.grid(row=2, column=0, sticky='s')
        self.lefthand.pack()
        self.righthandF.grid(row=2, column=2, sticky='s')
        self.righthand.pack()
        self.clothesF.grid(row=2, column=1)
        self.clothes.pack()
        self.cloakF.grid(row=2, column=3)
        self.cloak.pack()
        self.beltF.grid(row=3, column=1)
        self.belt.pack()
        self.pantsF.grid(row=4, column=1)
        self.pants.pack()
        self.leftbootF.grid(row=5, column=0)
        self.leftboot.pack()
        self.rightbootF.grid(row=5, column=2)
        self.rightboot.pack()
        ######
        # self.buttons.grid(row=6, column=1)
        # self.do_equip.grid(row=0, column=0)
        # self.un_equip.grid(row=0, column=1)

    def equip(self, item=None, **kwargs):
        slotmap = {'glove': ['lefthand', 'righthand'],
                   'belt': ['belt'],
                   'lightarmor': ['clothes', 'pants'],
                   'mediumarmor': ['clothes', 'pants'],
                   'heavyarmor': ['clothes', 'pants'],
                   'clothes': ['clothes', 'pants'],
                   'headwear': ['head'],
                   'boots': ['leftboot', 'rightboot'],
                   'necklace': ['neck'],
                   'cloak': ['cloak'],
                   'shield': [],
                   None: []}
        if (item):
            t = item.get('type')
            if (isinstance(t, str)):
                t = t.lower()
            n = item.name
            # Change the item to register as equipped
            item.equipped = t
        else:
            try:
                t = kwargs['slot'].lower()
                n = kwargs['name']
            except KeyError:
                raise
        if t not in slotmap:
            print(t)
            raise KeyError
        for (key, val) in self.registry.items():
            if (val == slotmap[t]):
                # if the slot is occupied,
                # automatically replace the existing item (maybe change this)
                del self.registry[key]
                break
        for i in slotmap[t]:
            l = self.__getattribute__(i)
            f = self.__getattribute__(i + 'F')
            l.config(text=n, bg='#FFAAAA')
            f.config(bg='#FFAAAA')
        self.registry[n] = slotmap[t]

    def unequip(self, item=None, **kwargs):
        if (item):
            n = item.name
            item.equipped = ''
        else:
            try:
                n = kwargs['name']
            except KeyError:
                raise
        if (n in self.registry):
            for i in self.registry[n]:
                l = self.__getattribute__(i)
                f = self.__getattribute__(i + 'F')
                l.config(text='', bg=self.basecolor)
                f.config(bg=self.basecolor)
            del self.registry[n]

    def toggle_equip(self, item):
        if (item.name in self.registry):
            self.unequip(item)
        else:
            self.equip(item)


class module(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container)
        self.character = character
        self.buttonframe = tk.Frame(self.f)
        self.handler = self.character.inventory
        self.display = EquipmentDisplay(self.f)
        self.buttons = []
        for item in self.handler:
            if (item.type in ['weapon', 'ranged weapon', 'apparel']):
                self.buttons.append(tk.Button(self.buttonframe, text=item.name, command=lambda x=item: self.display.toggle_equip(x)))
                if (item.equipped):
                    self.display.equip(item)
        self.draw_static()

    def draw_static(self):
        self.buttonframe.grid(row=0, column=0)
        s = 5
        for i, b in enumerate(self.buttons):
            b.grid(row=i%s, column=i//s)
        self.display.grid(row=0, column=1)


class main(gui.Section):
    def __init__(self, window):
        gui.Section.__init__(self, window)
        self.display = EquipmentDisplay(self.f)
        self.buttonframe = tk.Frame(self.f)
        self.QUIT = tk.Button(self.f, text='QUIT', command=self.writequit,
                              fg='red')
        self.startup_begin()

    def draw_static(self):
        self.buttonframe.grid(row=0, column=0)
        s = 5
        for i, b in enumerate(self.buttons):
            b.grid(row=i%s, column=i//s)
        self.display.grid(row=0, column=1)
        self.QUIT.grid(row=1, column=2)

    def startup_begin(self):
        self.charactername = {}
        gui.Query(self.charactername, self.startup_finish, 'Character Name?')
        self.container.withdraw()

    def startup_finish(self):
        name = self.charactername['Character Name?']
        path = iface.JSONInterface.OBJECTSPATH + 'character/' + name + '.character'
        if (os.path.exists(path)):
            self.record = iface.JSONInterface(path)
        else:
            raise FileNotFoundError
        self.handler = c.Inventory(self.record)
        self.buttons = []
        for item in self.handler:
            self.buttons.append(tk.Button(self.buttonframe, text=item.name, command=lambda x=item: self.display.toggle_equip(x)))
            if (item.equipped):
                self.display.equip(item)
        self.draw_static()
        self.container.deiconify()

    def writequit(self):
        self.record.write()
        self.container.destroy()


if __name__ == '__main__':
    win = gui.MainWindow()
    iface.JSONInterface.OBJECTSPATH = os.path.dirname(os.path.abspath(__file__)) + '/../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
