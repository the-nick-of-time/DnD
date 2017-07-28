import tkinter as tk

# import tools.forge.classes as c
# import tools.forge.helpers as h
# import tools.forge.GUIbasics as gui
# import tools.libraries.tkUtility as util
# import tools.libraries.rolling as r
# import tools.forge.interface as iface
import classes as c
import helpers as h
import GUIbasics as gui
import tkUtility as util
import rolling as r
import interface as iface


class HitDiceDisplay(gui.ResourceDisplay):
    def __init__(self, container, resource, parent, parentwidget):
        gui.ResourceDisplay.__init__(self, container, resource)
        self.parent = parent
        self.parentwidget = parentwidget

    def decrement(self):
        self.parent.use_HD(self.resource.value)
        self.draw_dynamic()
        self.parentwidget.draw_dynamic()


class HitPointDisplay(gui.Section):
    def __init__(self, container, handler):
        gui.Section.__init__(self, container)
        self.handler = handler
        ################
        self.hpsection = tk.Frame(self.f)
        ################
        self.numbers = tk.Frame(self.hpsection)
        self.hplabel = tk.Label(self.numbers, text='HP')
        self.currentvalue = tk.StringVar()
        self.currentvalue.trace('w', lambda a,b,c: self.update_hp())
        self.current = tk.Entry(self.numbers, textvariable=self.currentvalue,
                                width=7)
        self.plus = tk.Label(self.numbers, text='+')
        self.templabel = tk.Label(self.numbers, text='Temp HP')
        self.tempvalue = tk.StringVar()
        self.tempvalue.trace('w', lambda a,b,c: self.update_temp())
        self.temp = tk.Entry(self.numbers, textvariable=self.tempvalue,
                             width=7)
        self.slash = tk.Label(self.numbers, text='/')
        self.mxlabel = tk.Label(self.numbers, text='Max HP')
        self.mxvalue = tk.StringVar()
        self.mxvalue.trace('w', lambda a,b,c: self.update_maxhp())
        self.mx = tk.Entry(self.numbers, textvariable=self.mxvalue, width=7)
        ################
        self.buttonframe = tk.Frame(self.hpsection)
        self.deltavalue = tk.StringVar()
        self.delta = tk.Entry(self.buttonframe, textvariable=self.deltavalue,
                              width=10)
        self.delta.bind('<Return>', lambda event: self.change_HP())
        self.change = tk.Button(self.buttonframe, text='Change HP',
                                command=lambda: self.change_HP())
        self.tempchange = tk.Button(self.buttonframe, text='Add Temp HP',
                                    command=lambda: self.change_temp())
        ###############
        self.hdsection = tk.Frame(self.f)
        self.hddisplays = [HitDiceDisplay(self.hdsection, self.handler.hd[key], self.handler, self) for key in self.handler.hd]
        ###############
        self.draw_static()
        self.draw_dynamic()

    def change_HP(self):
        self.handler.change_HP(self.deltavalue.get())
        self.draw_dynamic()

    def change_temp(self):
        self.handler.temp_HP(self.deltavalue.get())
        self.draw_dynamic()

    def draw_static(self):
        self.hpsection.grid(row=0, column=0)
        #############
        self.numbers.grid(row=0, column=0)
        self.hplabel.grid(row=0, column=0)
        self.current.grid(row=1, column=0)
        self.plus.grid(row=1, column=1)
        self.templabel.grid(row=0, column=2)
        self.temp.grid(row=1, column=2)
        self.slash.grid(row=1, column=3)
        self.mxlabel.grid(row=0, column=4)
        self.mx.grid(row=1, column=4)
        #############
        self.buttonframe.grid(row=1, column=0)
        self.delta.grid(row=0, column=0)
        self.change.grid(row=0, column=1)
        self.tempchange.grid(row=0, column=2)
        #############
        self.hdsection.grid(row=0, column=1)
        for (i, item) in enumerate(self.hddisplays):
            item.grid(row=0, column=i)

    def draw_dynamic(self):
        self.currentvalue.set(self.handler.get_HP())
        self.mxvalue.set(self.handler.get_max())
        self.tempvalue.set(self.handler.get_temp())

    def update_maxhp(self):
        self.handler.set_max(int(self.mxvalue.get() or 0))

    def update_hp(self):
        self.handler.set_hp(int(self.currentvalue.get() or 0))

    def update_temp(self):
        self.handler.set_temp(int(self.tempvalue.get() or 0))

    def long_rest(self):
        self.handler.rest('long')


class main(gui.Section):
    def __init__(self, container, jf):
        gui.Section.__init__(self, container)
        self.record = jf
        self.corehandler = c.HPhandler(jf)
        self.hpdisplay = HitPointDisplay(self.f, self.corehandler)
        self.auxhandlers = self.corehandler.hd.values()
        # self.hddisplays = [HitDiceDisplay(self.f, item, self.corehandler) for item in self.auxhandlers]
        self.QUIT = tk.Button(self.f, command=self.writequit, text='QUIT')
        self.draw_static()

    def draw_static(self):
        self.hpdisplay.grid(row=0, column=0)
        # for (i, a) in enumerate(self.auxhandlers):
        #     self.hddisplays[i].grid(0, i+1)
        self.QUIT.grid(row=1, column=0)

    def writequit(self):
        print(self.corehandler.hd['1d8'].number)
        print(self.record.get('/HP/HD/1d8'))
        self.corehandler.write()
        self.container.destroy()


# class HitPointDisplay(gui.ResourceDisplay):
#     def __init__(self, container, handler):
#         handler.name = 'HP'
#         handler.value = 1
#         gui.ResourceDisplay.__init__(container, handler)
#         self.plus = tk.Label(self.numbers, text='+')
#         self.tempvalue = tk.StringVar()
#         self.temp = tk.Entry(self.numbers, textvariable=self.tempvalue)


# class main(gui.Element, gui.Section):
#     def __init__(self, container):
#         kwargs = {'name': 'hp', 'container': container}
#         gui.Section.__init__(self, **kwargs)
#         gui.Element.__init__(self, **kwargs)
#         self.popup()
#         self.create_widgets()
#
#     def create_widgets(self):
#         self.max = util.labeledEntry(self.f, 'Maximum HP', 0, 0, width=5)
#         self.current = util.labeledEntry(self.f, 'Current HP', 0, 1, width=5)
#         self.amount = util.labeledEntry(self.f,
#                                         'HP Change\nas integer or roll',
#                                         2,
#                                         0,
#                                         width=10,
#                                         orient='h')
#         self.amount.bind('<Return>', lambda event: self.changeHP(False))
#         self.temp = util.labeledEntry(self.f, '+Temporary HP', 0, 2, width=5)
#         buttons = tk.Frame(self.f, pady=15)
#         buttons.grid(row=2, column=2)
#         self.alterHP = tk.Button(buttons,
#                                  text='Alter\nHP',
#                                  command=lambda: self.changeHP(False))
#         self.alterHP.grid(row=0, column=0)
#         self.addtemp = tk.Button(buttons,
#                                  text='Add to\ntemp HP',
#                                  command=lambda: self.changeHP(True))
#         self.addtemp.grid(row=0, column=1)
#         HDf = tk.Frame(self.f)
#         HDf.grid(row=3, column=1)
#         self.HD = [HitDiceDisplay(t, HDf, self.handler)]
#         self.QUIT = tk.Button(self.f, text='QUIT',
#                               command=lambda: self.writequit())
#         self.QUIT.grid(row=4, column=3)
#
#     def popup(self):
#         def extract():
#             loadCharacter(name.get())
#             self.classes = ClassMap(self.character.get('/classes'))
#             self.populate()
#             self.draw()
#             subwin.destroy()
#
#         def loadCharacter(name):
#             filename = 'character/' + h.clean(name) + '.character'
#             self.character = iface.JSONInterface(filename)
#         subwin = tk.Toplevel()
#         name = util.labeledEntry(subwin, 'Character name', 0, 0)
#         accept = tk.Button(subwin, text='Accept', command=lambda: extract())
#         accept.grid(row=1, column=1)
#
#     def changeHP(self, totemp=False):
#         amount = int(r.call(self.amount.get()))
#         h = int(self.current.get())
#         t = int(self.temp.get())
#         m = int(self.max.get())
#         if (totemp):
#             t += amount
#         else:
#             if (amount < 0):
#                 if (abs(amount) > t):
#                     amount += t
#                     t = 0
#                     h += amount
#                 else:
#                     t += amount
#             else:
#                 h += amount
#                 h = m if h > m else h
#         util.replaceEntry(self.temp, str(t))
#         util.replaceEntry(self.current, str(h))
#
#     def populate(self):
#         util.replaceEntry(self.max, self.character.get('/HP/max'))
#         util.replaceEntry(self.current, self.character.get('/HP/current'))
#         util.replaceEntry(self.temp, self.character.get('/HP/temp'))
#
#     def draw(self):
#         self.grid(0, 0)
#
#     def writequit(self):
#         self.character.set('/HP/max', int(self.max.get()))
#         self.character.set('/HP/current', int(self.current.get()))
#         self.character.set('/HP/temp', int(self.temp.get()))
#         self.character.write()
#         self.container.destroy()
#
#
# class HitDiceDisplay(gui.Section, gui.Element):
#     def __init__(self, name, container, handler):
#         kwargs = {'name': 'hp', 'container': container}
#         gui.Section.__init__(self, **kwargs)
#         gui.Element.__init__(self, **kwargs)
#         self.manager = handler
#         self.type = name
#
#     def create_widgets(self):
#         # self.inc = tk.Button(self.f, text='+', command=self.regain)
#         self.use = tk.Button(self.f, text='Use',
#                              command=lambda: self.handler.use_HD(self.type))
#         self.typeL = tk.Label(self.f, text=self.handler.hdtype)
#         self.number = tk.Label(self.f)
#
#     def draw(self):
#         self.typeL.grid(row=0, column=0)
#         self.number.grid(row=0, column=1)
#         self.use.grid(row=0, column=2)
#
#
# class HP:
#     def __init__(self, jf):
#         self.iface = jf
#         self.current = jf.get('/current')
#         self.max = jf.get('/max')
#         self.temp = jf.get('/temp')
#         self.truemax = jf.get('/truemax')
#
#     def change(self, amount):
#         delta = r.roll(amount)
#         if (delta < 0):
#             delta = self.temp(delta)
#         self.HP += delta
#         if (self.HP > self.max):
#             self.HP = self.max
#         elif (self.HP < 0):
#             self.HP = 0
#
#     def changeMax(self, amount):
#         delta = r.roll(amount)
#         self.max += delta
#
#     def temp(self, amount):
#         # Returns the spillover
#         delta = r.roll(amount)
#         if (delta < 0):
#             if (-delta >= self.temp):
#                 delta += self.temp
#                 self.temp = 0
#                 return delta
#             else:
#                 self.temp += delta
#                 delta = 0
#                 return delta
#         else:
#             self.temp = delta if delta > self.temp else self.temp
#             delta = 0
#             return delta
#
#     def short_rest(self):
#         self.temp = 0
#
#     def long_rest(self):
#         self.max = self.truemax
#         self.current = self.max
#         self.temp = 0
#
#     def writequit(self):
#         self.iface.write()
#
#
# class HD:
#     def __init__(self, jf):
#         pass
#
#     def use(self):
#         pass
#
#     def short_rest(self):
#         pass
#
#     def long_rest(self):
#         pass
#
#     def writequit(self):
#         pass

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
    iface.JSONInterface.OBJECTSPATH = '../objects/'
    character = iface.JSONInterface('character/Calan.character')
    app = main(win, character)
    app.pack()
    win.mainloop()
