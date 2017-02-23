import tkinter as tk
import math

import tools.forge.classes as c
import tools.forge.helpers as h
import tools.forge.GUIbasics as gui
import tools.libraries.tkUtility as util
import tools.libraries.rolling as r
import tools.forge.interface as iface
from tools.forge.ClassMap import ClassMap
import tools.forge.hd as hd


class main(gui.Element, gui.Section):
    def __init__(self, container):
        kwargs = {'name': 'hp', 'container': container}
        gui.Section.__init__(self, **kwargs)
        gui.Element.__init__(self, **kwargs)
        self.popup()
        self.create_widgets()

    def create_widgets(self):
        self.max = util.labeledEntry(self.f, 'Maximum HP', 0, 0, width=5)
        self.current = util.labeledEntry(self.f, 'Current HP', 0, 1, width=5)
        self.amount = util.labeledEntry(self.f,
                                        'HP Change\nas integer or roll',
                                        2,
                                        0,
                                        width=10,
                                        orient='h')
        self.amount.bind('<Return>', lambda event: self.changeHP(False))
        self.temp = util.labeledEntry(self.f, '+Temporary HP', 0, 2, width=5)
        buttons = tk.Frame(self.f, pady=15)
        buttons.grid(row=2, column=2)
        self.alterHP = tk.Button(buttons,
                                 text='Alter\nHP',
                                 command=lambda: self.changeHP(False))
        self.alterHP.grid(row=0, column=0)
        self.addtemp = tk.Button(buttons,
                                 text='Add to\ntemp HP',
                                 command=lambda: self.changeHP(True))
        self.addtemp.grid(row=0, column=1)
        HDf = tk.Frame(self.f)
        HDf.grid(row=3, column=1)
        self.HD = [HitDiceDisplay(t, HDf, self.handler)]
        self.QUIT = tk.Button(self.f, text='QUIT',
                              command=lambda: self.writequit())
        self.QUIT.grid(row=4, column=3)

    def popup(self):
        def extract():
            loadCharacter(name.get())
            self.classes = ClassMap(self.character.get('/classes'))
            self.populate()
            self.draw()
            subwin.destroy()

        def loadCharacter(name):
            filename = 'character/' + h.clean(name) + '.character'
            self.character = iface.JSONInterface(filename)
        subwin = tk.Toplevel()
        name = util.labeledEntry(subwin, 'Character name', 0, 0)
        accept = tk.Button(subwin, text='Accept', command=lambda: extract())
        accept.grid(row=1, column=1)

    def changeHP(self, totemp=False):
        amount = int(r.call(self.amount.get()))
        h = int(self.current.get())
        t = int(self.temp.get())
        m = int(self.max.get())
        if (totemp):
            t += amount
        else:
            if (amount < 0):
                if (abs(amount) > t):
                    amount += t
                    t = 0
                    h += amount
                else:
                    t += amount
            else:
                h += amount
                h = m if h > m else h
        util.replaceEntry(self.temp, str(t))
        util.replaceEntry(self.current, str(h))

    def populate(self):
        util.replaceEntry(self.max, self.character.get('/HP/max'))
        util.replaceEntry(self.current, self.character.get('/HP/current'))
        util.replaceEntry(self.temp, self.character.get('/HP/temp'))

    def draw(self):
        self.grid(0, 0)

    def writequit(self):
        self.character.set('/HP/max', int(self.max.get()))
        self.character.set('/HP/current', int(self.current.get()))
        self.character.set('/HP/temp', int(self.temp.get()))
        self.character.write()
        self.container.destroy()


class HitDiceDisplay(gui.Section, gui.Element):
    def __init__(self, name, container, handler):
        kwargs = {'name': 'hp', 'container': container}
        gui.Section.__init__(self, **kwargs)
        gui.Element.__init__(self, **kwargs)
        self.manager = handler
        self.type = name

    def create_widgets(self):
        # self.inc = tk.Button(self.f, text='+', command=self.regain)
        self.use = tk.Button(self.f, text='Use',
                             command=lambda: self.handler.use_HD(self.type))
        self.typeL = tk.Label(self.f, text=self.handler.hdtype)
        self.number = tk.Label(self.f)

    def draw(self):
        self.typeL.grid(row=0, column=0)
        self.number.grid(row=0, column=1)
        self.use.grid(row=0, column=2)


class HP:
    def __init__(self, jf):
        self.iface = jf
        self.current = jf.get('/current')
        self.max = jf.get('/max')
        self.temp = jf.get('/temp')
        self.truemax = jf.get('/truemax')

    def change(self, amount):
        delta = r.roll(amount)
        if (delta < 0):
            delta = self.temp(delta)
        self.HP += delta
        if (self.HP > self.max):
            self.HP = self.max
        elif (self.HP < 0):
            self.HP = 0

    def changeMax(self, amount):
        delta = r.roll(amount)
        self.max += delta

    def temp(self, amount):
        # Returns the spillover
        delta = r.roll(amount)
        if (delta < 0):
            if (-delta >= self.temp):
                delta += self.temp
                self.temp = 0
                return delta
            else:
                self.temp += delta
                delta = 0
                return delta
        else:
            self.temp = delta if delta > self.temp else self.temp
            delta = 0
            return delta

    def short_rest(self):
        self.temp = 0

    def long_rest(self):
        self.max = self.truemax
        self.current = self.max
        self.temp = 0

    def writequit(self):
        self.iface.write()


class HD:
    def __init__(self, jf):
        pass

    def use(self):
        pass

    def short_rest(self):
        pass

    def long_rest(self):
        pass

    def writequit(self):
        pass

# class MultiHitDiceDisplay(gui.Section, gui.Element):
#     def __init__(self, name, container, character):
#         kwargs = {'name': 'hp', 'container': container}
#         gui.Section.__init__(self, **kwargs)
#         gui.Element.__init__(self, **kwargs)
#         self.name = name
#         self.container = container
#         self.character = character
#         self.manager = hd.MultiHandler(character)
#         self.subdisplays = []
#
#     def create_widgets(self):
#         for handler in self.manager.hd.values():
#             self.subdisplays.append(SingleHitDiceDisplay(handler))
#         self.rest = tk.Button(self.f, text='Long Rest', command=self.manager.rest)
#         self.reset = tk.Button(self.f, text='Reset all', command=self.manager.reset)
#
#     def draw(self):
#         for i, sub in enumerate(self.subdisplays):
#             sub.grid(row=i, column=0)
#         self.rest.grid(row=len(self.subdisplays), column=0, sticky='e')
#         self.reset.grid(row=len(self.subdisplays) + 1, column=0, sticky='e')


if __name__ == '__main__':
    win = tk.Tk()
    app = main(win)
    win.mainloop()
