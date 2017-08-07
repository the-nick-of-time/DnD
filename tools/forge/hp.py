import tkinter as tk
import os

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
        self.restframe = tk.Frame(self.f)
        # does nothing intentionally
        self.shortrest = tk.Button(self.restframe, text='Short rest')
        self.longrest = tk.Button(self.restframe, text='Long rest', command=self.long_rest)
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
        ############
        self.buttonframe.grid(row=1, column=0)
        self.shortrest.grid(row=0, column=0)
        self.longrest.grid(row=0, column=1)

    def draw_dynamic(self):
        self.currentvalue.set(self.handler.current)
        self.mxvalue.set(self.handler.max)
        self.tempvalue.set(self.handler.temp)

    def update_maxhp(self):
        self.handler.max = int(self.mxvalue.get() or 0)

    def update_hp(self):
        self.handler.current = int(self.currentvalue.get() or 0)

    def update_temp(self):
        self.handler.temp = int(self.tempvalue.get() or 0)

    def long_rest(self):
        self.handler.rest('long')
        for item in self.hddisplays:
            item.draw_dynamic()
        self.draw_dynamic()


class main(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.charactername = {}
        self.QUIT = tk.Button(self.f, command=self.writequit, text='QUIT')
        self.buttons = tk.Frame(self.f)
        self.longrest = tk.Button(self.buttons, text='Long Rest',
                                  command=self.long_rest)
        # Does nothing on purpose
        self.shortrest = tk.Button(self.buttons, text='Short Rest')
        self.startup_begin()

    def startup_begin(self):
        gui.Query(self.charactername, self.startup_finish, 'Character Name?')
        self.container.withdraw()

    def startup_finish(self):
        name = self.charactername['Character Name?']
        path = iface.JSONInterface.OBJECTSPATH + 'character/' + name + '.character'
        if (os.path.exists(path)):
            self.record = iface.JSONInterface(path)
        else:
            raise FileNotFoundError
        self.corehandler = c.HPhandler(self.record)
        self.hpdisplay = HitPointDisplay(self.f, self.corehandler)
        self.draw_static()
        self.container.deiconify()

    def draw_static(self):
        self.hpdisplay.grid(row=0, column=0)
        self.buttons.grid(row=1, column=0)
        self.shortrest.grid(row=0, column=0)
        self.longrest.grid(row=0, column=1)
        self.QUIT.grid(row=1, column=1)

    def long_rest(self):
        self.hpdisplay.long_rest()

    def writequit(self):
        self.corehandler.write()
        self.container.destroy()


if (__name__ == '__main__'):
    win = tk.Tk()
    iface.JSONInterface.OBJECTSPATH = '../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
