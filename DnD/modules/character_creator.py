#! /usr/bin/env python3

import json
import os
import re
import sys
import tkinter as tk
import tkinter.messagebox as messagebox
from collections import OrderedDict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '/../libraries'))

import lib.components as gui
import lib.interface as iface
import lib.helpers as h
import lib.classmap as cm
from levelup import FeaturesAtLevel


class BasicInfoSelector(gui.Section):
    def __init__(self, container, raceupdated, classupdated):
        gui.Section.__init__(self, container)
        # TODO: make listboxes that automatically show options for races and
        #   classes that have files associated with them
        self.raceL = tk.Label(self.f, text='Race?')
        self.racename = tk.StringVar()
        self.racename.trace('w', lambda a, b, c: raceupdated(self.racename))
        # self.race = tk.Entry(self.f)
        races = ['Dwarf (Hill)', 'Dwarf (Mountain)', 'Elf (High)',
                 'Elf (Wood)', 'Gnome (Forest)', 'Gnome (Rock)', 'Half-Elf',
                 'Half-Orc', 'Halfling (Lightfoot)', 'Halfling (Stout)',
                 'Human', 'Nephilim', 'Orc', 'Selkie', 'Tiefling',
                 'Dragonborn (Black)', 'Dragonborn (Blue)',
                 'Dragonborn (Brass)', 'Dragonborn (Bronze)',
                 'Dragonborn (Copper)', 'Dragonborn (Gold)',
                 'Dragonborn (Green)', 'Dragonborn (Red)',
                 'Dragonborn (Silver)', 'Dragonborn (White)']
        self.race = tk.OptionMenu(self.f, self.racename, *races)
        self.clL = tk.Label(self.f, text='Class?')
        # self.cl = tk.Entry(self.f)
        classes = ['Bard', 'Barbarian', 'Cleric', 'Druid', 'Fighter', 'Monk',
                   'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock',
                   'Wizard']
        self.classname = tk.StringVar()
        self.classname.trace('w', lambda a, b, c: classupdated(self.classname))
        self.cl = tk.OptionMenu(self.f, self.classname, *classes)
        self.langL = tk.Label(self.f, text='Languages?')
        self.lang = tk.Entry(self.f)
        self.draw_static()

    def draw_static(self):
        for (i, name) in enumerate(['race', 'cl', 'lang']):
            self.__getattribute__(name + 'L').grid(row=i, column=0)
            self.__getattribute__(name).grid(row=i, column=1)

    def export(self):
        data = OrderedDict()
        # data['race'] = self.race.get()
        data['race'] = self.racename.get()
        # data['level'] = self.cl.get() + ' 1'
        data['level'] = self.classname.get() + ' 1'
        data['languages'] = re.split(',\s*', self.lang.get())
        return data


class AbilitySelector(gui.Section):
    abilnames = ['Strength', 'Dexterity', 'Constitution',
                 'Intelligence', 'Wisdom', 'Charisma']

    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.names = [tk.Label(self.f, text=n[:3].upper())
                      for n in self.abilnames]
        self.scores = [tk.Entry(self.f, width=3) for _ in self.abilnames]
        self.savebools = [tk.BooleanVar() for _ in self.abilnames]
        self.saves = [tk.Checkbutton(self.f, text='Save Proficiency?',
                                     variable=self.savebools[i])
                      for (i, a) in enumerate(self.abilnames)]
        self.draw_static()

    def draw_static(self):
        for (i, a) in enumerate(self.abilnames):
            self.names[i].grid(row=i, column=0)
            self.scores[i].grid(row=i, column=1)
            self.saves[i].grid(row=i, column=2)

    def export(self):
        data = OrderedDict()
        data['abilities'] = {}
        data['saves'] = []
        for (i, a) in enumerate(self.abilnames):
            data['abilities'][a] = int(self.scores[i].get())
            if self.savebools[i].get():
                data['saves'].append(a)
        return data


class SkillSelector(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        sk = iface.JsonInterface('skill/SKILLS.skill')
        self.skillmap = sk.get('/')
        self.proficiencies = [tk.StringVar() for _ in self.skillmap]
        self.buttons = [tk.Checkbutton(self.f, text=n,
                                       variable=self.proficiencies[i],
                                       onvalue=n, offvalue='')
                        for (i, n) in enumerate(sorted(self.skillmap))]
        self.draw_static()

    def draw_static(self):
        for (i, obj) in enumerate(self.buttons):
            obj.grid(row=i // 3, column=i % 3)

    def export(self):
        data = OrderedDict()
        data['skills'] = []
        for (i, s) in enumerate(self.skillmap):
            prof = self.proficiencies[i].get()
            if prof != '':
                data['skills'].append(prof)
        return data


class RaceFeaturesDisplay(gui.Section):
    def __init__(self, container, features):
        gui.Section.__init__(self, container)
        self.displays = []
        for name in features:
            self.displays.append(gui.EffectPane(self.f, name,
                                                features[name]['description']))
        self.draw_static()

    def draw_static(self):
        for (i, d) in enumerate(self.displays):
            d.grid(row=i, column=0)
            d.short_display.config(width=15, wraplength=100)


class Main(gui.Section):
    def __init__(self, window):
        gui.Section.__init__(self, window)
        # self.data = {}
        self.data = OrderedDict()
        self.featuresframe = tk.Frame(self.f)
        # self.NEXT = tk.Button(self.f, text='Select Features',
        #                       command=self.select_features)
        self.QUIT = tk.Button(self.f, text='QUIT', fg='red',
                              command=self.write_and_quit)
        self.startup_begin()

    def draw_static(self):
        self.basic.grid(row=0, column=0)
        self.featuresframe.grid(row=0, column=1)
        self.abils.grid(row=1, column=0)
        self.skills.grid(row=1, column=1)
        # self.NEXT.grid(row=5, column=2)
        self.QUIT.grid(row=5, column=3)

    def draw_dynamic(self):
        # self.features.grid(row=2, column=1)
        try:
            self.classfeatures.grid(row=0, column=1)
        except AttributeError:
            pass
        try:
            self.racefeatures.grid(row=0, column=0)
        except AttributeError:
            pass

    def startup_begin(self):
        self.charactername = {}
        gui.Query(self.charactername, self.startup_end, 'Character Name?')
        self.container.withdraw()

    def startup_end(self):
        self.name = self.charactername['Character Name?']
        self.container.title(self.name)
        path = 'character/' + h.clean(self.name) + '.character'
        self.filename = iface.JsonInterface.OBJECTSPATH / path
        if self.filename.exists():
            ok = messagebox.askokcancel(message='You are overwriting an '
                                                'existing file. Continue?')
            if not ok:
                self.container.destroy()

        f = open(self.filename, 'w')
        f.close()
        ######
        self.basic = BasicInfoSelector(self.f, self.race_features,
                                       self.class_features)
        self.abils = AbilitySelector(self.f)
        self.skills = SkillSelector(self.f)
        ######
        self.draw_static()
        self.container.deiconify()

    def class_features(self, var):
        classname = var.get()
        path = 'class/' + h.clean(classname) + '.class'
        classjf = iface.JsonInterface(path)
        self.classfeatures = FeaturesAtLevel(self.featuresframe, classjf, 1)
        self.draw_dynamic()

    def race_features(self, var):
        racename = var.get()
        raceobj = cm.RaceMap(racename)
        racejf = raceobj.record
        self.racefeatures = RaceFeaturesDisplay(self.featuresframe,
                                                racejf.get('*/features'))
        self.draw_dynamic()

    def export_features(self):
        # classfeatures = self.features.export()
        classfeatures = self.classfeatures.export()
        if 'SUBCLASS' in classfeatures:
            name = classfeatures.pop('SUBCLASS')
            other = classfeatures.pop('MAIN CLASS')
            classobj = cm.ClassMap(self.data['level'])
            classobj.apply_subclass(other, name)
            self.data['level'] = str(classobj)
        raceobj = cm.RaceMap(self.data['race'])
        racefeatures = raceobj.get_feature_links()
        features = OrderedDict()
        features.update(classfeatures)
        features.update(racefeatures)
        return {'features': features}

    def export_hp(self):
        classobj = cm.ClassMap(self.data['level'])
        rec = classobj[0]
        HD = rec.get('/hit_dice')
        maxhp = (int(HD[2:])
                 + h.modifier(self.data['abilities']['Constitution']))
        data = OrderedDict((('max', maxhp),
                            ('current', maxhp),
                            ('temp', 0),
                            ('HD', {HD: {'number': 1, 'maxnumber': 1}})))
        return {'HP': data}

    @staticmethod
    def export_empties():
        data = OrderedDict((('inventory', {}),
                            ('spell_slots', []),
                            ('spells_prepared', {'prepared_today': [],
                                                 'always_prepared': []})))
        return data

    def write_and_quit(self):
        self.data['name'] = self.name
        self.data.update(self.basic.export())
        self.data.update(self.abils.export())
        self.data.update(self.export_hp())
        self.data.update(self.skills.export())
        self.data.update(self.export_empties())
        self.data.update(self.export_features())
        with open(self.filename, 'w') as outfile:
            json.dump(self.data, outfile, indent=2)
        self.container.destroy()


if __name__ == '__main__':
    from pathlib import Path

    iface.JsonInterface.OBJECTSPATH = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / 'objects'
    win = gui.MainWindow()
    app = Main(win)
    app.pack()
    win.mainloop()
