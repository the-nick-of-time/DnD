#! /usr/bin/env python3

import os
import re
import sys
import tkinter as tk

sys.path.insert(0,
                os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import GUIbasics as gui
import interface as iface
import helpers as h
import classes as c
import rolling as r


class LimitedQueue:
    def __init__(self, num):
        self.num = num
        self.data = []

    def append(self, var):
        if var in self.data:
            return None
        if len(self.data) >= self.num:
            obj = self.data.pop(0)
            obj.set('')
        self.data.append(var)

    def remove(self, var):
        for (i, item) in enumerate(self.data):
            if item == var:
                del self.data[i]
                return True
        return False


class FeaturePicker(gui.Section):
    def __init__(self, container, fullpath, callback=None, locked=False):
        gui.Section.__init__(self, container)
        self.fullpath = fullpath
        self.record, self.path = h.path_follower(fullpath)
        data = self.record.get(self.path)
        self.name = self.path.split('/')[-1]
        self.callback = callback
        self.locked = locked
        self.nameL = tk.Label(self.f, text=self.name)
        self.desc = gui.InfoButton(self.f, data['description'], self.name)
        self.selected = tk.StringVar()
        if not self.locked:
            clb = lambda: self.callback(self.selected)
            self.selector = tk.Checkbutton(self.f, variable=self.selected,
                                           command=clb, onvalue=self.name,
                                           offvalue='')
        else:
            self.selected.set(self.name)
        self.draw_static()

    def draw_static(self):
        if not self.locked:
            self.selector.grid(row=0, column=0)
        self.nameL.grid(row=0, column=1)
        self.desc.grid(row=0, column=2)

    def export(self):
        if self.selected.get():
            return {self.name: self.fullpath}
        else:
            return {}


class Chooser(gui.Section):
    def __init__(self, container, fullpath):
        gui.Section.__init__(self, container)
        self.fullpath = fullpath
        jf, path = h.path_follower(fullpath)
        self.data = jf.get(path)
        num = self.data['number']
        self.f = tk.LabelFrame(self.container, text='Choose ' + str(num))
        self.wrapper = tk.Frame(self.f)
        self.queue = LimitedQueue(num)
        self.selectors = []
        for n in self.data:
            if n != 'number':
                self.selectors.append(FeaturePicker(self.wrapper,
                                                    self.fullpath + '/' + n,
                                                    self.register_change))
        self.draw_static()

    def draw_static(self):
        self.wrapper.grid(row=0, column=0)
        for (i, item) in enumerate(self.selectors):
            item.grid(row=i, column=0)

    def register_change(self, var):
        if var.get():
            self.queue.append(var)
        else:
            self.queue.remove(var)

    def export(self):
        rv = {}
        for item in self.selectors:
            rv.update(item.export())
        return rv


class SubclassChooser(Chooser):
    def __init__(self, container, fullpath):
        Chooser.__init__(self, container, fullpath)
        self.subfeatures = tk.Frame(self.f)
        self.subfeatures.grid(row=len(self.selectors), column=0)

    # noinspection PyAttributeOutsideInit
    def register_change(self, var):
        Chooser.register_change(self, var)
        self.subclassname = var.get()
        if self.subclassname:
            # Add the subclass and display extra options
            clm = re.search('(\w+)\.class', self.fullpath)
            self.classname = clm.group(1)
            name = 'class/{}.{}.sub.class'.format(h.clean(self.classname),
                                                  h.clean(self.subclassname))
            if os.path.isfile(iface.JSONInterface.OBJECTSPATH + name):
                self.clear_subframe()
                rec = iface.JSONInterface(name)
                lvm = re.search('/(\d+)/.*$', self.fullpath)
                lv = int(lvm.group(1))
                self.subclassFeatures = FeaturesAtLevel(self.subfeatures, rec, lv)
                self.draw_dynamic()
            else:
                raise FileNotFoundError(name)

    def clear_subframe(self):
        for w in self.subfeatures.winfo_children():
            w.destroy()

    def draw_dynamic(self):
        self.subclassFeatures.grid(row=1, column=0)

    def export(self):
        rv = Chooser.export(self)
        rv.update(self.subclassFeatures.export())
        rv['SUBCLASS'] = self.subclassname
        rv['MAIN CLASS'] = self.classname
        return rv


class FeaturesAtLevel(gui.Section):
    def __init__(self, container, jf, level):
        gui.Section.__init__(self, container)
        self.genPath = '{}/features/' + str(level)
        self.data = jf.get(self.genPath.format('*'))
        self.subframes = []
        for item in jf:
            val = item.get(self.genPath.format(''))
            if val is not None:
                for n in val:
                    fullpath = self.genPath.format('class/' + str(item))
                    if n == 'choose':
                        obj = Chooser(self.f, fullpath + '/choose')
                    elif n == 'subclass':
                        obj = SubclassChooser(self.f, fullpath + '/subclass')
                    else:
                        obj = FeaturePicker(self.f, fullpath + '/' + n,
                                            locked=True)
                    self.subframes.append(obj)
        self.draw_static()

    def draw_static(self):
        for (i, item) in enumerate(self.subframes):
            item.grid(row=i, column=0)

    def export(self):
        rv = {}
        for item in self.subframes:
            rv.update(item.export())
        return rv


class Module(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container)
        self.character = character
        self.choice = tk.StringVar()

    def ask_level_begin(self):
        window = tk.Toplevel()
        classes = ['Bard', 'Barbarian', 'Cleric', 'Druid', 'Fighter', 'Monk',
                   'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock',
                   'Wizard']
        menu = tk.OptionMenu(window, self.choice, *classes)
        menu.grid(row=0, column=0)
        accept = tk.Button(window, text='Continue', command=self.ask_level_end)
        accept.grid(row=0, column=1)

    # noinspection PyAttributeOutsideInit
    def ask_level_end(self):
        cl = self.choice.get()
        # ask for class name to level up
        pattern = r'\s*([a-zA-Z\']+)\s*(\(([a-zA-Z\'\s]+)\))?'
        desc_ = re.match(pattern, cl).groups()
        desc = [str(item) for item in desc_ if item is not None]
        # desc should be a class and possibly a subclass name
        (rec, level) = self.character.classes.level_up(*desc)
        self.core = FeaturesAtLevel(self.f, rec.record, level)
        self.draw_static()

    def draw_static(self):
        self.core.grid(row=0, column=0)

    def write(self):
        # Not really sure how to modularize this as it should have a common interface?
        # Or maybe not; it will have to take over from character manager anyway
        features = self.core.export()
        if 'SUBCLASS' in features:
            name = features.pop('SUBCLASS')
            other = features.pop('MAIN CLASS')
            self.character.classes.apply_subclass(other, name)
        self.container.destroy()
        currentFeatures = self.character.get('/features')
        currentFeatures.update(features)
        self.character.set('/features', currentFeatures)
        self.character.write()


class Main(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.QUIT = tk.Button(self.f, text='QUIT', fg='red',
                              command=self.write_quit)
        # self.draw_static()
        self.startup_begin()

    # noinspection PyAttributeOutsideInit
    def startup_begin(self):
        self.levelGain = {}
        classes = ['Bard', 'Barbarian', 'Cleric', 'Druid', 'Fighter', 'Monk',
                   'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock',
                   'Wizard']
        gui.CharacterQuery(self.levelGain, self.startup_end,
                           ['Class to gain a level in?', classes],
                           ['Average or roll for HP?', ['average', 'roll']])
        self.container.withdraw()

    # noinspection PyAttributeOutsideInit
    def startup_end(self):
        name = self.levelGain['Character Name?']
        cl = self.levelGain['Class to gain a level in?']
        path = 'character/' + h.clean(name) + '.character'
        if os.path.exists(iface.JSONInterface.OBJECTSPATH + path):
            self.record = iface.JSONInterface(path)
        else:
            gui.ErrorMessage('A character with that name was not found.')
        if not os.path.exists(iface.JSONInterface.OBJECTSPATH + path):
            gui.ErrorMessage('A class with that name was not found.')
        self.character = c.Character(self.record)
        pattern = r'\s*([a-zA-Z\']+)\s*(\(([a-zA-Z\'\s]+)\))?'
        desc_ = re.match(pattern, cl).groups()
        desc = [str(item) for item in desc_ if item is not None]
        # desc should be a class and possibly a subclass name
        (rec, level) = self.character.classes.level_up(*desc)
        self.core = FeaturesAtLevel(self.f, rec.record, level)
        # Set new number of hit dice
        size = rec.hit_dice
        hdPath = '/HP/HD/' + size + '/maxnumber'
        hdn = self.character.get(hdPath)
        self.character.set(hdPath, hdn + 1)
        # Set new number of hit points
        conmod = h.modifier(self.character.get('/abilities/Constitution'))
        if self.levelGain['Average or roll for HP?'] == 'average':
            gain = r.roll(size, 'average') + .5
        elif self.levelGain['Average or roll for HP?'] == 'roll':
            gain = r.roll(size)
        current = self.character.get('/HP/max')
        # noinspection PyUnboundLocalVariable
        self.character.set('/HP/max', current + gain + conmod)
        self.draw_static()
        self.container.deiconify()

    def draw_static(self):
        self.core.grid(0, 0)
        self.QUIT.grid(row=1, column=0)

    def write_quit(self):
        features = self.core.export()
        if 'SUBCLASS' in features:
            name = features.pop('SUBCLASS')
            other = features.pop('MAIN CLASS')
            self.character.classes.apply_subclass(other, name)
        self.container.destroy()
        currentFeatures = self.character.get('/features')
        currentFeatures.update(features)
        self.character.set('/features', currentFeatures)
        self.character.write()


if __name__ == '__main__':
    win = gui.MainWindow()
    iface.JSONInterface.OBJECTSPATH = os.path.dirname(os.path.abspath(__file__)) + '/../objects/'
    app = Main(win)
    app.pack()
    win.mainloop()
