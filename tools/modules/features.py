#! /usr/bin/env python3

import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import components as gui
import classes as c
import interface as iface


class FeaturesDisplay(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container)
        self.displays = []
        for f in character.features:
            self.displays.append(gui.EffectPane(self.f, f.name, str(f)))
        self.draw_static()

    def draw_static(self):
        s = 10
        for (i, d) in enumerate(self.displays):
            d.grid(row=i%s, column=i//s)


class module(FeaturesDisplay):
    def __init__(self, container, character):
        FeaturesDisplay.__init__(self, container, character)
        self.f.config(bd=2, relief='groove')


class main(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.QUIT = tk.Button(self.f, text='QUIT', fg='red', command=self.quit)
        self.startup_begin()

    def draw_static(self):
        self.core.grid(row=0, column=0)
        self.QUIT.grid(row=1, column=1)

    def startup_begin(self):
        self.charactername = {}
        gui.Query(self.charactername, self.startup_end, 'Character Name?')
        self.container.withdraw()

    def startup_end(self):
        name = self.charactername['Character Name?']
        path = 'character/' + name + '.character'
        if (os.path.exists(iface.JSONInterface.OBJECTSPATH + path)):
            self.record = iface.JSONInterface(path)
        else:
            raise FileNotFoundError
        self.character = c.Character(self.record)
        self.core = FeaturesDisplay(self.f, self.character)
        self.draw_static()
        self.container.deiconify()

    def quit(self):
        self.container.destroy()


if (__name__ == '__main__'):
    win = gui.MainWindow()
    iface.JSONInterface.OBJECTSPATH = os.path.dirname(os.path.abspath(__file__)) + '/../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
