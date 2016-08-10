import tkinter as tk
import json
import re
import collections
import sys

import tools.forge.helpers as h
import tools.forge.GUIbasics as gui
import tools.libraries.tkUtility as util


class main(gui.Element, gui.Section):
    def __init__(self, container):
        gui.Element.__init__(self, 'inventory')
        gui.Section.__init__(self, container)

        self.mainframe = tk.Frame(self.f)

        names_ = ['item', 'treasure', 'weapon', 'armor']
        frames_ = [tk.LabelFrame(self.mainframe, text=pluralize(n).upper())
                   for n in names_]

        self.frames = collections.OrderedDict()
        self.frames.update(zip(names_, frames_))

        self.carried = tk.Label(self.f)
        self.encumbrance = tk.Label(self.f)

        self.popup()

    def loadCharacter(self, name):
        filename = 'character/' + clean(name) + '.character'
        self.character = JSONInterface(filename)

    def totalWeight(self):
        weight_ = 0
        for item in self.items:
            weight_ += item.character['quantity'] * item.details.get('/weight')
        self.carryWeight = weight_

    def strengthAnalysis(self):
        strength = self.character.get('/abilities/Strength')
        stages = ["no penalty.",
                  "speed drops by 10 feet.",
                  "Speed drops by 20 feet and disadvantage on physical rolls.",
                  "cannot carry, can push.",
                  "cannot move."]
        thresholds = [strength * 5,
                      strength * 10,
                      strength * 15,
                      strength * 30,
                      sys.maxsize]
        for s, t in zip(stages, thresholds):
            if self.carryWeight <= t:
                return s

    def loadItems(self):
        allitems = self.character.get('/inventory')
        self.items = []
        for item in allitems:
            t = item['type'].split('.')[-1]
            self.items.append(ItemDisplay(self.frames[t], item))

    def draw(self):
        self.grid(row=0, column=0)
        self.mainframe.grid(row=0, column=0)
        for i, (n, f) in enumerate(self.frames.items()):
            f.grid(row=0, column=i, sticky='n')
        for i, item in enumerate(self.items):
            item.grid(row=i, column=0)
        self.carried['text'] = self.totalWeight()
        self.encumbrance['text'] = self.strengthAnalysis()
        self.carried.grid(row=1, column=0)
        self.encumbrance.grid(row=1, column=1)

    def popup(self):
        def extract():
            self.loadCharacter(name.get())
            self.loadItems()
            subwin.destroy()
            self.draw()
        subwin = tk.Toplevel()
        name = util.labeledEntry(subwin, 'Character name', 0, 0)
        accept = tk.Button(subwin, text='Accept', command=lambda: extract())
        accept.grid(row=1, column=1)

    def writequit(self):
        self.character.write()


class ItemDisplay(gui.Element, gui.Section):
    PATHPREFIX = '/inventory'

    def __init__(self, container, character):
        # character is the JSONInterface object
        gui.Element.__init__(self, character['name'])
        gui.Section.__init__(self, container)

        self.character = character

        self.namedisplay = tk.Label(self.f, text=self.character['name'])

        self.numcontainer = tk.Frame(self.f)
        self.numdisplay = tk.Label(self.numcontainer,
                                   text=self.character['quantity'])
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

        self.draw()

    def make(self):
        self.details = hook(self.character)
        self.isReal = self.details is not None

    def draw(self):
        self.namedisplay.grid(row=0, column=0)
        self.numcontainer.grid(row=1, column=0)
        self.numdisplay.grid(row=0, column=0)
        self.increment.grid(row=0, column=1)
        self.decrement.grid(row=0, column=2)
        if (self.isReal):
            self.dispeffect.grid(row=3, column=0)
            self.numbers.grid(row=2, column=0)
            self.weight.grid(row=0, column=0)
            self.value.grid(row=0, column=1)

    def num(self, change):
        self.character['quantity'] += change
        self.numdisplay['text'] = self.character['quantity']
        self.draw()


class JSONInterface:
    OBJECTSPATH = './tools/objects/'

    def __init__(self, filename):
        self.filename = self.OBJECTSPATH + filename
        with open(self.filename) as f:
            data = json.load(f)
            self.info = data

    def get(self, path, root=None):
        try:
            if (root is None):
                return self.get(path, self.info)
            comp = path.split(sep='/', maxsplit=1)
            if (len(comp) == 1):
                # Terminal
                return root[conv(comp[0])]
            if (comp[0] == ''):
                # Intitial
                return self.get(comp[1], self.info)
            # Recurse
            return self.get(comp[1], root[conv(comp[0])])
        except (KeyError, IndexError):
            return ""

    def set(self, path, value, root=None):
        try:
            if (root is None):
                return self.set(path, value, self.info)
            comp = path.split(sep='/', maxsplit=1)
            if (len(comp) == 1):
                # Terminal
                root[conv(comp[0])] = value
                return True
            if (comp[0] == ''):
                # Intitial
                return self.set(comp[1], value, self.info)
            # Recurse
            return self.set(comp[1], value, root[conv(comp[0])])
        except (KeyError, IndexError):
            return False

    def write(self):
        with open(self.filename) as f:
            json.dump(obj=self.info, fp=f)


def conv(val):
    try:
        return int(val)
    except ValueError:
        return val


def hook(item):
    directory = '{direc}/{name}'
    location = item['type'].split(sep='.')
    if (location[0] == ''):
        # Leading . indicates name of object is included in path
        location[0] = clean(item['name'])
    filename = directory.format(direc=location[-1],
                                name='.'.join(location))
    try:
        out = JSONInterface(filename)
    except FileNotFoundError:
        out = None
    return out


def pluralize(name):
    if (name == 'item' or name == 'weapon'):
        return name + 's'
    else:
        return name


def clean(name):
    return name.replace(' ', '_').replace('\'', '-')


if __name__ == '__main__':
    window = tk.Tk()
    app = Main(window)
    window.mainloop()
