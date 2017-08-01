import tkinter as tk
from os.path import isfile
from collections import OrderedDict
import json

import GUIbasics as gui
import interface as iface
import helpers as h


class ItemCreator(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.nameL = tk.Label(self.f, text='Name')
        self.name = tk.Entry(self.f)
        self.typeL = tk.Label(self.f, text='Type')
        self.type = tk.Entry(self.f)
        self.valueL = tk.Label(self.f, text='Value')
        self.value = tk.Entry(self.f)
        self.weightL = tk.Label(self.f, text='Weight')
        self.weight = tk.Entry(self.f)
        self.consumableL = tk.Label(self.f, text='Consumable')
        self.consumable = tk.BooleanVar()
        self.consumableE = tk.Checkbutton(self.f, variable=self.consumable)
        self.descriptionL = tk.Label(self.f, text='Description')
        self.description = tk.Text(self.f, height=4, width=50, wrap='word')
        self.effectL = tk.Label(self.f, text='Effect')
        self.effect = tk.Text(self.f, height=4, width=50, wrap='word')
        ##########
        self.draw_static()

    def draw_static(self):
        self.nameL.grid(row=0, column=0)
        self.name.grid(row=0, column=1)
        self.typeL.grid(row=1, column=0)
        self.type.grid(row=1, column=1)
        self.valueL.grid(row=2, column=0)
        self.value.grid(row=2, column=1)
        self.weightL.grid(row=3, column=0)
        self.weight.grid(row=3, column=1)
        self.consumableL.grid(row=4, column=0)
        self.consumableE.grid(row=4, column=1)
        self.descriptionL.grid(row=5, column=0)
        self.description.grid(row=5, column=1)
        self.effectL.grid(row=6, column=0)
        self.effect.grid(row=6, column=1)

    def write(self):
        data = OrderedDict((('name', self.name.get()),
                ('value', self.value.get()),
                ('weight', self.weight.get()),
                ('consumable', self.consumable.get()),
                ('description', self.description.get('1.0', 'end')),
                ('effect', self.effect.get('1.0', 'end')),
                ))
        t = self.type.get().split()[-1]
        path = '{b}{t}/{n}.{t}'.format(b=iface.JSONInterface.OBJECTSPATH,
                                       t=t, n=h.clean(data['name']))
        if (isfile(path)):
            raise FileExistsError
        with open(path, 'w') as outfile:
            json.dump(data, outfile, indent=2)


class main(gui.Section):
    def __init__(self, container):
        gui.Section.__init__(self, container)
        self.handler = ItemCreator(self.f)
        self.another = tk.Button(self.f, text='Another', command=self.another)
        self.QUIT = tk.Button(self.f, text='QUIT', command=self.quit)
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        self.another.grid(row=1, column=1)
        self.QUIT.grid(row=2, column=1)

    def draw_dynamic(self):
        self.handler.grid(0, 0)

    def another(self):
        self.handler.write()
        self.handler.f.destroy()
        self.handler = ItemCreator(self.f)
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
