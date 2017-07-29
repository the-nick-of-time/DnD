import tkinter as tk
import re
from collections import OrderedDict
import sys
import os

import helpers as h
import GUIbasics as gui
from interface import JSONInterface
import classes as c
import tkUtility as util
from helpers import clean


class ItemDisplay(gui.Section):
    def __init__(self, container, handler):
        gui.Section.__init__(self, container)
        self.item = handler
        ######
        self.name = tk.Label(self.f, text=self.item.name)
        ######
        self.interact = tk.Frame(self.f)
        self.numbervalue = tk.StringVar()
        self.numbervalue.trace('w', callback=lambda a,b,c: self.set_number())
        self.number = tk.Entry(self.interact, textvariable=self.numbervalue,
                               width=5)
        self.usebutton = tk.Button(self.interact, text='Use', command=self.use)
        self.increment = tk.Button(self.interact, text='+', command=lambda: self.change(1))
        self.decrement = tk.Button(self.interact, text='-', command=lambda: self.change(-1))
        ######
        self.numbers = tk.Frame(self.f)
        self.weight = tk.Label(self.numbers)
        self.value = tk.Label(self.numbers)
        ######
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        self.name.grid(row=0, column=0)
        ######
        self.interact.grid(row=1, column=0)
        self.number.grid(row=0, column=0)
        self.usebutton.grid(row=0, column=1)
        self.increment.grid(row=0, column=2)
        self.decrement.grid(row=0, column=3)
        ######
        self.numbers.grid(row=2, column=0)
        self.weight.grid(row=0, column=0)
        self.value.grid(row=0, column=1)
        ######
        self.describe()
        self.numbervalue.set(self.item.number)

    def draw_dynamic(self):
        self.weight['text'] = '{w} lb'.format(w=self.total_weight())
        self.value['text'] = '{v} gp'.format(v=self.total_value())

    def total_weight(self):
        return self.item.weight * self.item.number

    def total_value(self):
        return self.item.value * self.item.number

    def use(self):
        effect = self.item.use()
        if (effect):
            self.effect = gui.EffectPane(self.f, h.shorten(effect), effect)
            self.effect.grid(row=4, column=0)

    def describe(self):
        desc = self.item.describe()
        if (desc):
            self.description = gui.EffectPane(self.f, h.shorten(desc), desc)
            self.description.grid(row=3, column=0)

    def set_number(self):
        num = self.numbervalue.get()
        self.item.number = int(num or 0)

    def change(self, amount):
        current = int(self.numbervalue.get() or 0)
        self.numbervalue.set(str(current + amount))


class InventoryHandler(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.characterdata = {}
        self.newitemdata = {}
        self.frameframe = tk.Frame(self.f)
        self.framenames = ['item', 'treasure', 'weapon', 'armor']
        self.coreframes = {n: tk.LabelFrame(self.frameframe,
                                            text=pluralize(n).upper(),
                                            bd=2, relief='ridge')
                           for n in self.framenames}
        self.objectblocks = {n: [] for n in self.framenames}
        self.totalinfo = tk.Frame(self.f)
        self.totalweight = tk.Label(self.totalinfo)
        self.encumbrance = tk.Label(self.totalinfo)
        self.newitem = tk.Button(self.totalinfo, text='New Item',
                                 command=self.new_item_start)
        ######
        self.load_character_start()
        self.draw_static()

    def draw_static(self):
        self.frameframe.grid(row=0, column=0)
        for (i, name) in enumerate(self.framenames):
            self.coreframes[name].grid(row=0, column=i)
        ######
        self.totalinfo.grid(row=1, column=0)
        self.totalweight.grid(row=0, column=0)
        self.encumbrance.grid(row=0, column=1)
        self.newitem.grid(row=0, column=2)

    def draw_dynamic(self):
        for block in self.objectblocks.values():
            print(block)
            for (i, item) in enumerate(block):
                item.grid(row=i, column=0)
        self.encumbrance['text'] = self.strength_analysis()
        self.totalweight['text'] = 'Current load: {}'.format(self.total_weight())

    def load_character_start(self):
        popup = gui.Query(self.characterdata, self.load_character_end,
                          'Character name?')

    def load_character_end(self):
        name = self.characterdata['Character name?']
        path = JSONInterface.OBJECTSPATH + 'character/' + name + '.character'
        print(path)
        if (os.path.exists(path)):
            self.character = JSONInterface(path)
        else:
            raise FileNotFoundError
        self.handler = c.Inventory(self.character)
        for (name, item) in self.handler:
            t = item.type.split()[-1]
            self.objectblocks[t].append(ItemDisplay(self.coreframes[t], item))
        self.draw_dynamic()

    def new_item_start(self):
        gui.Query(self.newitemdata, self.new_item_end, 'Name?', 'Quantity?', 'Type?', 'Equipped?')

    def new_item_end(self):
        i = self.newitemdata
        self.handler.newslot(i['Name?'], int(i['Quantity?']), i['Type?'],
                             bool(i['Equipped?']))
        self.draw_dynamic()

    def total_weight(self):
        s = 0
        for block in self.objectblocks.values():
            for item in block:
                s += item.total_weight()
        return s

    def strength_analysis(self):
        strength = self.character.get('/abilities/strength')
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
        carryWeight = self.total_weight()
        for s, t in zip(stages, thresholds):
            if (carryWeight <= t):
                return s

    def write(self):
        self.handler.write()


class main(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.inv = InventoryHandler(self.f)
        self.inv.grid(0, 0)
        self.QUIT = tk.Button(self.f, text='QUIT', command=self.quit)
        self.QUIT.grid(row=1, column=1)

    def quit(self):
        self.inv.write()
        self.container.destroy()


def pluralize(name):
    if (name == 'item' or name == 'weapon'):
        return name + 's'
    else:
        return name


if __name__ == '__main__':
    window = tk.Tk()
    JSONInterface.OBJECTSPATH = '../objects/'
    app = main(window)
    app.pack()
    window.mainloop()
