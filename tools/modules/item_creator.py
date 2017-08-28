#! /usr/bin/env python3

import tkinter as tk
import os
from os.path import isfile
from collections import OrderedDict
import json
import re
import sys
sys.path.insert(0,
                os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import GUIbasics as gui
import interface as iface
import helpers as h
import tkUtility as util


class Creator(gui.Section):
    """Subclasses must implement:
        basepath: str, formatted to create the path to the item
        """
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.basepath = ''
        self.name = gui.AskLine(self.f, 'Name', "The item's name.",
                                lambda m: tk.Entry(m))
        __class__.draw_static(self)

    def draw_static(self):
        self.name.pack()

    def export(self):
        return OrderedDict([('name', self.name.get())])

    def write(self):
        data = self.export()
        name = h.clean(data['name'])
        if (not name):
            raise FileNotFoundError
        path = iface.JSONInterface.OBJECTSPATH + self.basepath.format(name)
        if (isfile(path)):
            proceed = tk.messagebox.askyesno(message='You are overwriting an'
                                             ' existing file.\nContinue'
                                             ' anyway?')
            if (not proceed):
                raise FileExistsError(path)
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent=2)


class ItemCreator(Creator):
    def __init__(self, container):
        Creator.__init__(self, container)
        self.basepath = 'item/{}.item'
        self.value = gui.AskLine(self.f, 'Value', "The item's value, in gp"
                                 " (decimals okay, fractions not).",
                                 lambda m: tk.Entry(m))
        self.weight = gui.AskLine(self.f, 'Weight', "The item's weight, in "
                                  "pounds (decimals okay, fractions not).",
                                  lambda m: tk.Entry(m))
        d = ("If using this item consumes some item, put that name here. For"
             " instance, if you are making an item for ale, you would put "
             "'ale' here because using it means that you are consuming the "
             "ale. Alternatively, a lantern would consume 'oil', and a bow "
             "would consume 'arrow's.")
        self.consumes = gui.AskLine(self.f, 'Consumes', d,
                                    lambda m: tk.Entry(m))
        desc = lambda m: tk.Text(m, height=4, width=50, wrap='word')
        pull = lambda w: w.get('1.0', 'end').strip()
        self.description = gui.AskLine(self.f, 'Description', "A description "
                                       "of the item.", desc, pull)
        effc = lambda m: tk.Text(m, height=4, width=50, wrap='word')
        pull = lambda w: w.get('1.0', 'end').strip()
        self.effect = gui.AskLine(self.f, 'Effect', "What happens when you "
                                  "use the item.", effc, pull)
        __class__.draw_static(self)

    def draw_static(self):
        Creator.draw_static(self)
        self.value.pack()
        self.weight.pack()
        self.consumes.pack()
        self.description.pack()
        self.effect.pack()

    def export(self):
        rv = Creator.export(self)
        rv.update([('value', float(self.value.get())),
                   ('weight', float(self.weight.get())),
                   ('description', self.description.get()),
                   ('effect', self.effect.get()),
                   ])
        con = self.consumes.get()
        if (con):
            rv.update([('consumes', con)])
        return rv


class WeaponCreator(ItemCreator):
    def __init__(self, container):
        ItemCreator.__init__(self, container)
        self.basepath = 'weapon/{}.weapon'
        self.damage = gui.AskLine(self.f, 'Damage',
                                  "The weapon's damage roll.",
                                  lambda m: tk.Entry(m))
        self.damagetype = gui.AskLine(self.f, 'Damage type', "The weapon's "
                                      "damage type.", lambda m: tk.Entry(m))
        abils = ['Strength', 'Dexterity', 'Dexterity or Strength']
        self.ability = tk.StringVar()
        self.abilityM = gui.AskLine(self.f, 'Ability', "The ability used to "
                                    "make attack and damage rolls.",
                                    lambda m: tk.OptionMenu(m, self.ability,
                                                            *abils),
                                    lambda w: self.ability.get().split(' or '))
        self.weapontype = tk.StringVar()
        tps = ['Simple', 'Martial']
        self.wptypeM = gui.AskLine(self.f, 'Weapon class',
                                   "Simple or martial.",
                                   lambda m: tk.OptionMenu(m, self.weapontype,
                                                           *tps),
                                   lambda w: self.weapontype.get())
        self.hands = tk.StringVar()
        h = ['one', 'two', 'versatile']
        self.handsM = gui.AskLine(self.f, 'Hands', "One-handed, two-handed, "
                                  "or versatile weapon.",
                                  lambda m: tk.OptionMenu(m, self.hands, *h),
                                  lambda w: self.hands.get())
        __class__.draw_static(self)

    def draw_static(self):
        ItemCreator.draw_static(self)
        self.damage.pack()
        self.damagetype.pack()
        self.abilityM.pack()
        self.wptypeM.pack()
        self.handsM.pack()

    def export(self):
        rv = ItemCreator.export(self)
        rv.update([('damage', self.damage.get()),
                   ('damage_type', self.damagetype.get()),
                   ('ability', self.abilityM.get()),
                   ('weapon_type', self.wptypeM.get()),
                   ('hands', self.handsM.get())
                   ])
        return rv


class RangedWeaponCreator(WeaponCreator):
    def __init__(self, container):
        WeaponCreator.__init__(self, container)
        self.basepath = 'weapon/{}.ranged.weapon'
        self.range = gui.AskLine(self.f, 'Range', "The weapon's range.",
                                 lambda m: tk.Entry(m))
        __class__.draw_static(self)

    def draw_static(self):
        WeaponCreator.draw_static(self)
        self.range.pack()

    def export(self):
        rv = WeaponCreator.export(self)
        rv.update([('range', self.range.get())])
        return rv


class ApparelCreator(ItemCreator):
    def __init__(self, container):
        ItemCreator.__init__(self, container)
        self.basepath = 'apparel/{}.apparel'
        self.slot = tk.StringVar()
        slots = ['Glove', 'Belt', 'LightArmor', 'MediumArmor', 'HeavyArmor',
                 'Clothes', 'Headwear', 'Boots', 'Necklace', 'Cloak',
                 'Shield']
        self.slotM = gui.AskLine(self.f, 'Apparel slot occupied', "Where do "
                                 "you wear this item?",
                                 lambda m: tk.OptionMenu(m, self.slot, *slots),
                                 lambda w: self.slot.get())
        __class__.draw_static(self)

    def draw_static(self):
        ItemCreator.draw_static(self)
        self.slotM.pack()

    def export(self):
        rv = ItemCreator.export(self)
        rv.update([('type', self.slotM.get())])
        return rv


class ArmorCreator(ApparelCreator):
    def __init__(self, container):
        ApparelCreator.__init__(self, container)
        self.basepath = 'apparel/{}.apparel'
        self.baseAC = gui.AskLine(self.f, 'Base AC', "The base number (do not "
                                  "include the dex mod addition) read from "
                                  "the AC column of the Armor table.",
                                  lambda m: tk.Entry(m))
        __class__.draw_static(self)

    def draw_static(self):
        ApparelCreator.draw_static(self)
        self.baseAC.pack()

    def export(self):
        rv = ApparelCreator.export(self)
        rv.update([('base_AC', int(self.baseAC.get()))])
        return rv


class ShieldCreator(ApparelCreator):
    def __init__(self, container):
        ApparelCreator.__init__(self, container)
        self.basepath = 'apparel/{}.apparel'
        self.slot.set('Shield')
        __class__.draw_static(self)

    def draw_static(self):
        ApparelCreator.draw_static(self)

    def export(self):
        rv = ApparelCreator.export(self)
        rv.update([('bonus', {'AC': 2})])
        return rv


class TreasureCreator(ItemCreator):
    def __init__(self, container):
        ItemCreator.__init__(self, container)
        self.basepath = 'treasure/{}.treasure'


class main(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        types = ['item', 'treasure', 'weapon', 'ranged weapon', 'apparel',
                 'armor', 'shield']
        self.type = tk.StringVar()
        self.type.trace('w', lambda a, b, c: self.type_select(self.type.get()))
        self.typeselector = tk.OptionMenu(self.f, self.type, *types)
        self.another = tk.Button(self.f, text='Another', command=self.another)
        self.QUIT = tk.Button(self.f, text='QUIT', command=self.quit)
        self.draw_static()

    def draw_static(self):
        self.typeselector.grid(row=1, column=0)
        self.another.grid(row=1, column=1)
        self.QUIT.grid(row=2, column=1)

    def draw_dynamic(self):
        self.handler.grid(0, 0)

    def type_select(self, t):
        tpmap = {'item': ItemCreator, 'treasure': ItemCreator,
                 'weapon': WeaponCreator, 'ranged weapon': RangedWeaponCreator,
                 'apparel': ApparelCreator, 'armor': ArmorCreator,
                 'shield': ShieldCreator}
        try:
            self.handler.destroy()
        except AttributeError:
            pass
        self.handler = tpmap[t](self.f)
        self.draw_dynamic()

    def another(self):
        self.handler.write()
        self.type_select(self.type.get())
        self.draw_dynamic()

    def quit(self):
        self.handler.write()
        self.container.destroy()


if __name__ == '__main__':
    win = tk.Tk()
    iface.JSONInterface.OBJECTSPATH = '../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
