#! /usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import json
import re
import collections
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import GUIbasics as gui
import classes as c
import interface as iface
import helpers as h
import ClassMap as cm
from levelup import FeaturesAtLevel

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# import abilities


class BasicInfoSelector(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        # TODO: make listboxes that automatically show options for races and
        #   classes that have files associated with them
        self.raceL = tk.Label(self.f, text='Race?')
        self.race = tk.Entry(self.f)
        self.clL = tk.Label(self.f, text='Class?')
        self.cl = tk.Entry(self.f)
        self.langL = tk.Label(self.f, text='Languages?')
        self.lang = tk.Entry(self.f)
        self.draw_static()

    def draw_static(self):
        for (i, name) in enumerate(['race', 'cl', 'lang']):
            self.__getattribute__(name + 'L').grid(row=i, column=0)
            self.__getattribute__(name).grid(row=i, column=1)

    def export(self, data):
        data['race'] = self.race.get()
        data['level'] = self.cl.get() + ' 1'
        data['languages'] = re.split(',\s*', self.lang.get())


class AbilitySelector(gui.Section):
    abilnames = ['Strength', 'Dexterity', 'Constitution',
                 'Intelligence', 'Wisdom', 'Charisma']
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.names = [tk.Label(self.f, text=n[:3].upper()) for n in self.abilnames]
        self.scores = [tk.Entry(self.f, width=3) for n in self.abilnames]
        self.savebools = [tk.BooleanVar() for a in self.abilnames]
        self.saves = [tk.Checkbutton(self.f, text='Save Proficiency?', variable=self.savebools[i]) for (i, a) in enumerate(self.abilnames)]
        self.draw_static()

    def draw_static(self):
        for (i, a) in enumerate(self.abilnames):
            self.names[i].grid(row=i, column=0)
            self.scores[i].grid(row=i, column=1)
            self.saves[i].grid(row=i, column=2)

    def export(self, data):
        data['abilities'] = {}
        data['saves'] = []
        for (i, a) in enumerate(self.abilnames):
            data['abilities'][a] = int(self.scores[i].get())
            if (self.savebools[i].get()):
                data['saves'].append(a)


class SkillSelector(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        sk = iface.JSONInterface('skill/SKILLS.skill')
        self.skillmap = sk.get('/')
        self.proficiencies = [tk.StringVar() for n in sorted(self.skillmap)]
        self.buttons = [tk.Checkbutton(self.f, text=n, variable=self.proficiencies[i], onvalue=n, offvalue='') for (i, n) in enumerate(sorted(self.skillmap))]
        self.draw_static()

    def draw_static(self):
        for (i, obj) in enumerate(self.buttons):
            obj.grid(row=i//3, column=i%3)

    def export(self, data):
        data['skills'] = []
        for (i, s) in enumerate(self.skillmap):
            prof = self.proficiencies[i].get()
            if (prof != ''):
                data['skills'].append(prof)


class main(gui.Section):
    def __init__(self, window):
        gui.Section.__init__(self, window)
        # self.data = {}
        self.data = collections.OrderedDict()
        self.NEXT = tk.Button(self.f, text='Select Features', command=self.select_features)
        self.QUIT = tk.Button(self.f, text='QUIT', fg='red', command=self.writequit)
        self.startup_begin()

    def draw_static(self):
        self.basic.grid(row=0, column=0)
        self.abils.grid(row=1, column=0)
        self.skills.grid(row=1, column=1)
        self.NEXT.grid(row=5, column=2)
        self.QUIT.grid(row=5, column=3)

    def draw_dynamic(self):
        self.features.grid(row=2, column=1)

    def startup_begin(self):
        self.charactername = {}
        gui.Query(self.charactername, self.startup_end, 'Character Name?')

    def startup_end(self):
        self.name = self.charactername['Character Name?']
        self.container.title(self.name)
        path = 'character/' + h.clean(self.name) + '.character'
        self.filename = iface.JSONInterface.OBJECTSPATH + path
        if (os.path.exists(iface.JSONInterface.OBJECTSPATH + path)):
            ok = messagebox.askokcancel(message='You are overwriting an '
                                        'existing file. Continue?')
            if (not ok):
                raise FileExistsError

        f = open(self.filename, 'w')
        f.close()
        ######
        self.basic = BasicInfoSelector(self.f)
        self.abils = AbilitySelector(self.f)
        self.skills = SkillSelector(self.f)
        ######
        self.draw_static()

    def select_features(self):
        self.data['name'] = self.name
        self.basic.export(self.data)
        classes = cm.ClassMap(self.data['level'])
        # classname = classes._classes[0]
        # classjf = iface.JSONInterface('class/' + h.clean(classname) + '.class')
        classjf = classes[0].record
        self.features = FeaturesAtLevel(self.f, classjf, 1)
        self.draw_dynamic()

    def writequit(self):
        # self.data['name'] = self.name
        # self.basic.export(self.data)
        self.abils.export(self.data)
        self.skills.export(self.data)
        self.data['inventory'] = {}
        ######
        classes = cm.ClassMap(self.data['level'])
        classname = classes._classes[0]
        pathtoclass = 'class/' + h.clean(classname) + '.class'
        mainclass = iface.JSONInterface(pathtoclass)
        # mainfeatures = mainclass.get('/features/1')
        # features = {n: (pathtoclass + '/features/1/' + n) for n in mainfeatures}
        features = self.features.export()
        HD = mainclass.get('/hit_dice')
        maxhp = int(HD[2:]) + h.modifier(self.data['abilities']['Constitution'])
        HP = {'max': maxhp, 'current': maxhp, 'temp': 0, 'HD': {HD: {'number': 1, 'maxnumber': 1}}}
        self.data['HP'] = HP
        if (classes._subclasses[0] != ''):
            subclassname = h.clean(classes._subclasses[0])
            formatstr = 'class/{}.{}.sub.class'
            pathtosubclass = formatstr.format(classname, subclassname)
            'class/' + classname + '.' + h.clean(subclassname) + '.class'
            subclass = iface.JSONInterface(pathtosubclass)
            subfeatures = subclass.get('/features/1')
            # features.update({n: (pathtosubclass + '/features/1/' + n) for n in subfeatures})
        ######
        race = cm.RaceMap(self.data['race'])
        pathtorace = 'race/{}.race'.format(race.race)
        mainrace = iface.JSONInterface(pathtorace)
        mainfeatures = mainrace.get('/features') or {}
        features.update({n: (pathtorace + '/features/' + n) for n in mainfeatures})
        if (race.subrace != ''):
            pathtosubrace = 'race/{}.{}.sub.race'.format(race.race, race.subrace)
            subrace = iface.JSONInterface(pathtosubrace)
            subfeatures = subrace.get('/features') or {}
            features.update({n: (pathtosubrace + '/features/' + n) for n in subfeatures})
        #####
        self.data['features'] = features
        self.data['spells_prepared'] = {}
        self.data['spells_prepared']['prepared_today'] = []
        self.data['spells_prepared']['always_prepared'] = []
        self.data['spell_slots'] = []
        #####
        with open(self.filename, 'w') as outfile:
            json.dump(self.data, outfile, indent=2)
        self.container.destroy()

if (__name__ == '__main__'):
    win = tk.Tk()
    iface.JSONInterface.OBJECTSPATH = '../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
