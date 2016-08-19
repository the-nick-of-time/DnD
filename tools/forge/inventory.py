import tkinter as tk
import re
from collections import OrderedDict
import sys

import tools.forge.helpers as h
import tools.forge.GUIbasics as gui
from tools.forge.interface import JSONInterface
from tools.forge.classes import Inventory
import tools.libraries.tkUtility as util
from tools.forge.helpers import clean


class main(gui.Element, gui.Section):
    def __init__(self, container):
        gui.Element.__init__(self, 'inventory')
        gui.Section.__init__(self, container)

        self.window = container

        self.mainframe = tk.Frame(self.f)

        names_ = ['item', 'treasure', 'weapon', 'armor']
        frames_ = [tk.LabelFrame(self.mainframe, text=pluralize(n).upper())
                   for n in names_]

        self.frames = OrderedDict()
        self.frames.update(zip(names_, frames_))

        self.ADDNEW = [tk.Button(self.frames[n], text='Add new',
                                 command=lambda: Adder(self.frames[n], self,
                                                       self.character))
                       for n in names_]

        self.bottom = tk.Frame(self.f)
        self.carried = tk.Label(self.bottom)
        self.encumbrance = tk.Label(self.bottom)

        self.QUIT = tk.Button(self.f, text='QUIT',
                              command=lambda: self.writequit())

        self.popup()

    def loadCharacter(self, name):
        filename = 'character/' + clean(name) + '.character'
        self.character = JSONInterface(filename)

    def loadItems(self):
        allitems = self.character.get('/inventory')
        self.items = []
        for (name, item) in allitems.items():
            t = item['type'].split('.')[-1]
            self.items.append(ItemDisplay(self.frames[t], self,
                                          self.character, name))

    def draw(self):
        self.grid(row=0, column=0)
        self.mainframe.grid(row=0, column=0)
        for i, (n, f) in enumerate(self.frames.items()):
            f.grid(row=0, column=i, sticky='n')
            self.ADDNEW[i].grid(row=len(self.items), column=0)
        for i, item in enumerate(self.items):
            item.grid(row=i, column=0)
        self.bottom.grid(row=1, column=0)
        self.carried.grid(row=1, column=0)
        self.encumbrance.grid(row=1, column=1)
        self.QUIT.grid(row=3, column=3)

    def popup(self):
        def extract():
            self.loadCharacter(name.get())
            self.update(level=3)
            subwin.destroy()
        subwin = tk.Toplevel()
        name = util.labeledEntry(subwin, 'Character name', 0, 0)
        accept = tk.Button(subwin, text='Accept', command=lambda: extract())
        accept.grid(row=1, column=1)

    def totalWeight(self):
        weight_ = 0
        for item in self.items:
            qpath = '/inventory/{}/quantity'.format(item.name)
            temp = item.details.get('/weight')
            if (isinstance(temp, str) or temp is None):
                weight_ += 0
            else:
                weight_ += item.character.get(qpath) * temp
        self.carryWeight = weight_
        return weight_

    def strengthAnalysis(self):
        strength = self.character.get('/abilities/Strength')
        stages = ["No penalty.",
                  "Your speed drops by 10 feet.",
                  "Your speed drops by 20 feet and you have disadvantage on "
                  "all physical rolls.",
                  "You cannot carry this much weight, only push or drag it.",
                  "You cannot move this much weight."]
        thresholds = [strength * 5,
                      strength * 10,
                      strength * 15,
                      strength * 30,
                      sys.maxsize]
        for s, t in zip(stages, thresholds):
            if (self.carryWeight <= t):
                return s

    def writequit(self):
        self.character.write()
        self.window.destroy()

    def update(self, level=2):
        """1: draw; 2: calculate carry weight; 3: reload items;
        4: load character"""
        if (level >= 4):
            # self.loadCharacter(name.get())
            pass
        if (level >= 3):
            self.loadItems()
        if (level >= 2):
            weight_ = self.totalWeight()
            self.carried['text'] = 'Current load: {0:0.1f}'.format(weight_)
            self.encumbrance['text'] = self.strengthAnalysis()
        if (level >= 1):
            self.draw()


class Adder:
    def __init__(self, container, master, character):
        self.place = container
        self.master = master
        self.character = character

        self.win = tk.Toplevel()
        self.name = util.labeledEntry(self.win, 'Input item name', 0, 0,
                                      orient='h')
        self.quantity = util.labeledEntry(self.win, 'Input quantity', 1, 0,
                                          orient='h', width=5)
        self.type = util.labeledEntry(self.win, 'Input type', 2, 0,
                                      orient='h')
        self.typeHelp = gui.HelpButton(self.win, 'Put the file extension here.'
                                       ' For special cases like treasure, put '
                                       'the full file name.')
        self.typeHelp.grid(row=2, column=2)
        self.finalize = tk.Button(self.win, text='ADD',
                                  command=lambda: self.finish())
        self.finalize.grid(row=3, column=1)

    def finish(self):
        _inv = self.character.get('/inventory')
        _inv[self.name.get()] = OrderedDict(
            (('quantity', int(self.quantity.get())),
             ('type', self.type.get()),
             ('equipped', False)))
        self.master.update(level=3)
        self.win.destroy()


class ItemDisplay(gui.Element, gui.Section):
    # TODO: allow this to function without a file
    def __init__(self, container, master, character, name):
        # character is the JSONInterface object
        gui.Element.__init__(self, name)
        gui.Section.__init__(self, container)

        self.master = master
        self.character = character
        self.prefix = '/inventory/{}'.format(name)
        self.name = name

        self.namedisplay = tk.Label(self.f, text=self.name)

        self.numcontainer = tk.Frame(self.f)
        self.sv = tk.StringVar()
        self.sv.trace('w', callback=lambda name, index, mode:
                      self.callbacknum(self.sv))
        self.numdisplay = tk.Entry(self.numcontainer, width=5,
                                   textvariable=self.sv)
        self.increment = tk.Button(self.numcontainer, text='+',
                                   command=lambda: self.num(1))
        self.decrement = tk.Button(self.numcontainer, text='-',
                                   command=lambda: self.num(-1))

        self.make()

        if (self.isReal):
            e = self.details.get('/effect')
            self.dispeffect = gui.EffectPane(self.f, h.shorten(e), e)
            self.numbers = tk.Frame(self.f)
            self.weight = tk.Label(self.numbers,
                                   text=str(self.details.get('/weight'))
                                   + ' lb')
            self.value = tk.Label(self.numbers,
                                  text=str(self.details.get('/value')) + ' gp')
        if (self.character.get('{}/quantity'.format(self.prefix)) > 0):
            self.draw()

    def __str__(self):
        return self.name

    def make(self):
        self.details = hook(self.character.get(self.prefix), self.name)
        self.isReal = self.details is not None

    def draw(self):
        self.namedisplay.grid(row=0, column=0)
        self.numcontainer.grid(row=1, column=0)
        self.numdisplay.grid(row=0, column=0)
        self.increment.grid(row=0, column=1)
        self.decrement.grid(row=0, column=2)
        path = '{}/quantity'.format(self.prefix)
        util.replaceEntry(self.numdisplay, self.character.get(path))
        if (self.isReal):
            self.dispeffect.grid(row=3, column=0)
            self.numbers.grid(row=2, column=0)
            self.weight.grid(row=0, column=0)
            self.value.grid(row=0, column=1)

    def num(self, change):
        path = '{}/quantity'.format(self.prefix)
        current = self.character.get(path)
        self.character.set(path, current + change)
        self.draw()
        self.master.update()

    def callbacknum(self, var):
        path = '{}/quantity'.format(self.prefix)
        self.character.set(path, int(var.get()) if var.get() else 0)
        self.master.update()


def hook(item, name):
    directory = '{direc}/{name}'
    location = item['type'].split(sep='.')
    if (location[0] == ''):
        # Leading . indicates name of object is included in path
        location[0] = clean(name)
        deeper = False
    else:
        deeper = True
    filename = directory.format(direc=location[-1], name='.'.join(location))
    try:
        out = JSONInterface(filename, PREFIX=name if deeper else '')
    except FileNotFoundError:
        print(filename, ' not found')
        out = None
    return out


def pluralize(name):
    if (name == 'item' or name == 'weapon'):
        return name + 's'
    else:
        return name


if __name__ == '__main__':
    window = tk.Tk()
    app = Main(window)
    window.mainloop()
