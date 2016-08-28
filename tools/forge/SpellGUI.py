import tkinter as tk
from collections import namedtuple

import tools.forge.helpers as h
import tools.forge.GUIbasics as gui
from tools.forge.interface import JSONInterface
import tools.libraries.tkUtility as util


class IndividualDisplay(gui.Section, gui.Element):
    def __init__(self, container, spell):
        self.spell = spell
        kwargs = {"name": self.spell.get('/name'), "container": container}
        gui.Section.__init__(self, **kwargs)
        gui.Element.__init__(self, **kwargs)
        self.level = self.spell.get('/level')
        self.effect = self.spell.get('/effect')
        self.levelnamemap = ['cantrip', '1st-level', '2nd-level', '3rd-level',
                             '4th-level', '5th-level', '6th-level',
                             '7th-level', '8th-level', '9th-level']
        self.draw()

    def create_widgets(self, master):
        # static
        widgets = namedtuple('Widgets', ['nameL', 'sclvF', 'simplelevelL',
                                         'levelL', 'schoolL', 'timeL',
                                         'durationL', 'rangeL', 'componentsL',
                                         'previewL', 'fullL', 'detailsB',
                                         'castB'])
        self.f.config(bd=2, relief='sunken')
        widgets.nameL = tk.Label(master, text=self.spell.get('/name'))
        widgets.sclvF = tk.Frame(master)
        widgets.simplelevelL = tk.Label(widgets.sclvF, text='Level: ' + str(self.level))
        widgets.levelL = tk.Label(widgets.sclvF, text=self.levelnamemap[self.level])
        widgets.schoolL = tk.Label(widgets.sclvF, text=self.spell.get('/school'))
        widgets.timeL = tk.Label(master, text='Casting Time: ' + self.spell.get('/casting_time'))
        if (self.spell.get('/concentration')):
            dur_text = 'Duration: Concentration, up to ' + self.spell.get('/duration').lower()
        else:
            dur_text = 'Duration: ' + self.spell.get('/duration')
        widgets.durationL = tk.Label(master, text=dur_text)
        widgets.rangeL = tk.Label(master, text='Range: ' + self.spell.get('/range'))
        widgets.componentsL = tk.Label(master, text='Components: ' + self.spell.get('/components'))
        widgets.previewL = tk.Label(master, text=h.shorten(self.effect), width=16, wraplength=120)
        widgets.fullL = tk.Label(master, text=self.effect, width=60, wraplength=400)
        # interactive
        widgets.detailsB = tk.Button(master, text='Details', command=self.popup)
        widgets.castB = tk.Button(master, text='CAST', command=self.cast)
        return widgets

    def draw(self):
        widgets = self.create_widgets(self.f)
        widgets.nameL.grid(row=0, column=0)
        widgets.sclvF.grid(row=0, column=1)
        widgets.simplelevelL.grid(row=0, column=0)
        widgets.timeL.grid(row=1, column=0)
        widgets.detailsB.grid(row=1, column=1)
        widgets.rangeL.grid(row=2, column=0)
        widgets.previewL.grid(row=3, column=0)
        widgets.castB.grid(row=4, column=0)

    def popup(self):
        def breakdown():
            win.destroy()
        win = tk.Toplevel()
        widgets = self.create_widgets(win)
        widgets.nameL.grid(row=0, column=0)
        if (self.level):
            widgets.levelL.grid(row=0, column=0)
            widgets.schoolL.grid(row=0, column=1)
        else:
            widgets.schoolL.grid(row=0, column=0)
            widgets.levelL.grid(row=0, column=1)
        widgets.sclvF.grid(row=1, column=0)
        widgets.timeL.grid(row=2, column=0)
        widgets.rangeL.grid(row=3, column=0)
        widgets.componentsL.grid(row=4, column=0)
        widgets.durationL.grid(row=5, column=0)
        widgets.fullL.grid(row=6, column=0)
        close = tk.Button(win, text='Close', command=breakdown)
        close.grid(row=7, column=1)

    def cast(self):
        win = tk.Toplevel()
        widgets = self.create_widgets(win)
        widgets.fullL.grid(row=0, column=0)
        close = tk.Button(win, text='Close', command=lambda: win.destroy())
        close.grid(row=1, column=1)


class main:
    def __init__(self, master):
        self.win = master
        self.f = tk.Frame(self.win)
        self.query()

    def query(self):
        def extract():
            loadCharacter(name.get())
            self.create_widgets()
            self.draw()
            subwin.destroy()
        def loadCharacter(name):
            self.character = JSONInterface('character/' + h.clean(name)
                                           + '.character')
        subwin = tk.Toplevel()
        name = util.labeledEntry(subwin, 'Character name', 0, 0)
        accept = tk.Button(subwin, text='Accept', command=lambda: extract())
        accept.grid(row=1, column=1)

    def create_widgets(self):
        def loadSpell(name):
            jf = JSONInterface('spell/' + h.clean(name) + '.spell')
            return IndividualDisplay(self.f, jf)
        self.spells = [loadSpell(spell) for spell in self.character.get('/spells_prepared')]
        # for spell in self.character.get('/spells_prepared'):
        #     self.spells.append(loadSpell(spell))
        self.quit = tk.Button(self.f, text='QUIT', command=self.win.destroy)

    def draw(self):
        for (i, disp) in enumerate(self.spells):
            disp.grid(row=i % 3, column=i // 3)
        self.quit.grid(row=4, column=i // 3 + 1)
        self.f.grid(row=0, column=0)
