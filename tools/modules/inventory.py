#! /usr/bin/env python3

import itertools
import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import helpers as h
import components as gui
from interface import JsonInterface
import classes as c


class ItemDisplay(gui.Section):
    def __init__(self, container, handler, reporter):
        gui.Section.__init__(self, container)
        self.item = handler
        self.reporter = reporter
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
        self.numbervalue.set(self.get_number())
        self.weight['text'] = '{w:0.2f} lb'.format(w=self.total_weight())
        self.value['text'] = '{v:0.2f} gp'.format(v=self.total_value())
        self.reporter()

    def total_weight(self):
        return self.item.weight * self.item.number

    def total_value(self):
        return self.item.value * self.item.number

    def use(self):
        effect = self.item.use()
        if effect:
            self.effect = gui.EffectPane(self.f, h.shorten(effect), effect)
            self.effect.grid(row=4, column=0)
        self.numbervalue.set(self.item.number)

    def describe(self):
        desc = self.item.describe()
        if desc:
            self.description = gui.EffectPane(self.f, h.shorten(desc), desc)
            self.description.grid(row=3, column=0)

    def set_number(self):
        num = self.numbervalue.get()
        self.item.number = int(num or 0)
        self.draw_dynamic()

    def get_number(self):
        return self.item.number

    def change(self, amount):
        current = int(self.numbervalue.get() or 0)
        self.numbervalue.set(str(current + amount))
        self.draw_dynamic()


class InventoryHandler(gui.Section):
    def __init__(self, container, handler, character):
        gui.Section.__init__(self, container)
        self.handler = handler
        self.character = character
        self.newitemdata = {}
        self.frameframe = tk.Frame(self.f)
        self.framenames = ['item', 'treasure', 'weapon', 'apparel']
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
        for item in self.handler:
            t = item.type.split()[-1]
            self.objectblocks[t].append(ItemDisplay(self.coreframes[t], item, self.update_encumbrance))
        self.draw_static()
        self.draw_dynamic()

    def __iter__(self):
        return (item for item in itertools.chain(*self.objectblocks))

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
        s = 4
        for block in self.objectblocks.values():
            i = 0
            for item in block:
                if item.get_number() > 0:
                    item.grid(row=i % s, column=i // s)
                    i += 1
                    item.draw_dynamic()
        self.update_encumbrance()

    def update_encumbrance(self):
        # TODO: somehow needs to get called from the
        self.encumbrance['text'] = self.strength_analysis()
        self.totalweight['text'] = 'Current load: {0:0.2f}'.format(self.total_weight())

    def new_item_start(self):
        gui.Query(self.newitemdata, self.new_item_end, 'Name?', 'Quantity?', 'Type?', 'Equipped?')

    def new_item_end(self):
        i = self.newitemdata
        eq = i['Equipped?'].lower() not in ['false', 'no', 'n']
        self.handler.newslot(i['Name?'], int(i['Quantity?']), i['Type?'], eq)
        item = self.handler[i['Name?']]
        t = i['Type?'].split()[-1]
        self.objectblocks[t].append(ItemDisplay(self.coreframes[t], item, self.update_encumbrance))
        self.draw_dynamic()

    def total_weight(self):
        s = 0
        for block in self.objectblocks.values():
            for item in block:
                s += item.total_weight()
        return s

    def strength_analysis(self):
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
        carryWeight = self.total_weight()
        for s, t in zip(stages, thresholds):
            if carryWeight <= t:
                return s

    def set_owner(self, character):
        self.owner = character
        for item in self.handler:
            item.set_owner(character)

    def write(self):
        self.handler.write()


class Module(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container, width=900, height=500)
        self.character = character
        self.core = InventoryHandler(self.f, character.inventory,
                                     character.record)
        self.core.set_owner(character)
        self.draw_static()

    def draw_dynamic(self):
        self.core.draw_dynamic()

    def draw_static(self):
        self.core.grid(row=0, column=0)


class Main(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.characterdata = {}
        self.QUIT = tk.Button(self.f, text='QUIT', command=self.quit)
        self.QUIT.grid(row=1, column=1)
        self.load_character_start()

    def load_character_start(self):
        gui.Query(self.characterdata, self.load_character_end,
                  'Character name?')
        self.container.withdraw()

    def load_character_end(self):
        name = self.characterdata['Character name?']
        path = JsonInterface.OBJECTSPATH / 'character' / (name + '.character')
        if path.exists():
            character = JsonInterface(path, isabsolute=True)
        else:
            raise FileNotFoundError
        handler = c.Inventory(character)
        self.inv = InventoryHandler(self.f, handler, character)
        self.inv.grid(row=0, column=0)
        self.container.deiconify()

    def quit(self):
        self.inv.write()
        self.container.destroy()


def pluralize(name):
    if name == 'item' or name == 'weapon':
        return name + 's'
    else:
        return name


if __name__ == '__main__':
    from pathlib import Path

    JsonInterface.OBJECTSPATH = Path(os.path.dirname(os.path.abspath(__file__)) + '/../objects/')
    win = gui.MainWindow()
    app = Main(win)
    app.pack()
    win.mainloop()
