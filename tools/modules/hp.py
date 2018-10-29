#! /usr/bin/env python3

import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import classes as c
import GUIbasics as gui
import interface as iface


class HitDiceDisplay(gui.ResourceDisplay):
    def __init__(self, container, resource, parent, parentwidget):
        gui.ResourceDisplay.__init__(self, container, resource)
        self.parent = parent
        self.parentwidget = parentwidget

    def decrement(self):
        val = self.parent.use_HD(self.resource.value)
        self.display.config(text=str(val))
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
        self.currentvalue.trace('w', lambda x, y, z: self.update_hp())
        self.current = tk.Entry(self.numbers, textvariable=self.currentvalue,
                                width=7)
        self.plus = tk.Label(self.numbers, text='+')
        self.tempLabel = tk.Label(self.numbers, text='Temp HP')
        self.tempValue = tk.StringVar()
        self.tempValue.trace('w', lambda x, y, z: self.update_temp())
        self.temp = tk.Entry(self.numbers, textvariable=self.tempValue,
                             width=7)
        self.slash = tk.Label(self.numbers, text='/')
        self.maxLabel = tk.Label(self.numbers, text='Max HP')
        self.maxValue = tk.StringVar()
        self.maxValue.trace('w', lambda x, y, z: self.update_maxhp())
        self.mx = tk.Entry(self.numbers, textvariable=self.maxValue, width=7)
        ################
        self.buttonFrame = tk.Frame(self.hpsection)
        self.deltaValue = tk.StringVar()
        self.delta = tk.Entry(self.buttonFrame, textvariable=self.deltaValue,
                              width=10)
        self.delta.bind('<Return>', lambda event: self.change_HP())
        self.change = tk.Button(self.buttonFrame, text='Change HP',
                                command=lambda: self.change_HP())
        self.tempChange = tk.Button(self.buttonFrame, text='Add Temp HP',
                                    command=lambda: self.change_temp())
        ###############
        self.hdSection = tk.Frame(self.f)
        self.hdDisplays = [HitDiceDisplay(self.hdSection, self.handler.hd[key], self.handler, self) for key in
                           self.handler.hd]
        ###############
        self.restFrame = tk.Frame(self.f)
        # does nothing intentionally
        self.shortRest = tk.Button(self.restFrame, text='Short rest')
        self.longRest = tk.Button(self.restFrame, text='Long rest', command=self.long_rest)
        ###############
        self.draw_static()
        self.draw_dynamic()

    def change_HP(self):
        self.handler.change_HP(self.deltaValue.get())
        self.draw_dynamic()

    def change_temp(self):
        self.handler.temp_HP(self.deltaValue.get())
        self.draw_dynamic()

    def draw_static(self):
        self.hpsection.grid(row=0, column=0)
        #############
        self.numbers.grid(row=0, column=0)
        self.hplabel.grid(row=0, column=0)
        self.current.grid(row=1, column=0)
        self.plus.grid(row=1, column=1)
        self.tempLabel.grid(row=0, column=2)
        self.temp.grid(row=1, column=2)
        self.slash.grid(row=1, column=3)
        self.maxLabel.grid(row=0, column=4)
        self.mx.grid(row=1, column=4)
        #############
        self.buttonFrame.grid(row=1, column=0)
        self.delta.grid(row=0, column=0)
        self.change.grid(row=0, column=1)
        self.tempChange.grid(row=0, column=2)
        #############
        self.hdSection.grid(row=0, column=1)
        for (i, item) in enumerate(self.hdDisplays):
            item.grid(row=0, column=i)
        ############
        self.buttonFrame.grid(row=1, column=0)
        self.shortRest.grid(row=0, column=0)
        self.longRest.grid(row=0, column=1)

    def draw_dynamic(self):
        self.currentvalue.set(self.handler.current)
        self.maxValue.set(self.handler.max)
        self.tempValue.set(self.handler.temp)
        for d in self.hdDisplays:
            d.draw_dynamic()

    def update_maxhp(self):
        self.handler.max = int(self.maxValue.get() or 0)

    def update_hp(self):
        self.handler.current = int(self.currentvalue.get() or 0)

    def update_temp(self):
        self.handler.temp = int(self.tempValue.get() or 0)

    def long_rest(self):
        self.handler.rest('long')
        for item in self.hdDisplays:
            item.draw_dynamic()
        self.draw_dynamic()


class Module(HitPointDisplay):
    def __init__(self, container, character):
        HitPointDisplay.__init__(self, container, character.hp)
        self.f.config(bd=2, relief='groove', pady=5)


class Main(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.charactername = {}
        self.QUIT = tk.Button(self.f, command=self.write_quit, text='QUIT')
        self.buttons = tk.Frame(self.f)
        self.longRest = tk.Button(self.buttons, text='Long Rest',
                                  command=self.long_rest)
        # Does nothing on purpose
        self.shortRest = tk.Button(self.buttons, text='Short Rest')
        self.startup_begin()

    def startup_begin(self):
        gui.Query(self.charactername, self.startup_finish, 'Character Name?')
        self.container.withdraw()

    # noinspection PyAttributeOutsideInit
    def startup_finish(self):
        name = self.charactername['Character Name?']
        path = iface.JSONInterface.OBJECTSPATH + 'character/' + name + '.character'
        if os.path.exists(path):
            self.record = iface.JSONInterface(path)
        else:
            raise FileNotFoundError
        self.coreHandler = c.HPHandler(self.record)
        self.hpDisplay = HitPointDisplay(self.f, self.coreHandler)
        self.draw_static()
        self.container.deiconify()

    def draw_static(self):
        self.hpDisplay.grid(row=0, column=0)
        self.buttons.grid(row=1, column=0)
        self.shortRest.grid(row=0, column=0)
        self.longRest.grid(row=0, column=1)
        self.QUIT.grid(row=1, column=1)

    def long_rest(self):
        self.hpDisplay.long_rest()

    def write_quit(self):
        self.coreHandler.write()
        self.container.destroy()


if __name__ == '__main__':
    win = gui.MainWindow()
    iface.JSONInterface.OBJECTSPATH = os.path.dirname(os.path.abspath(__file__)) + '/../objects/'
    app = Main(win)
    app.pack()
    win.mainloop()
