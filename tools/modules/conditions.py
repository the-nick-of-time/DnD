import tkinter as tk
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import GUIbasics as gui
import helpers as h
import classes as c
import interface as iface


class ConditionsDisplay(gui.Section):
    def __init__(self, container, character):
        gui.Section.__init__(self, container)
        self.character = character
        self.block = tk.Frame(self.f)
        self.buttons = {}
        noninteractable = ('exhaustion1', 'exhaustion2', 'exhaustion3',
                           'exhaustion4', 'exhaustion5', 'exhaustion6')
        for name in set(h.condition_defs) - set(noninteractable):
            self.buttons[name] = tk.Button(self.block, text=name.capitalize(), command=lambda x=name: self.toggle_condition(x))
        self.ex = tk.Frame(self.block)
        self.addexhaustion = tk.Button(self.ex, text='Add Exhaustion', command=lambda: self.exhaustion('add'))
        self.removeexhaustion = tk.Button(self.ex, text='Remove Exhaustion', command=lambda: self.exhaustion('remove'))
        self.exhaustionlevel = tk.Label(self.ex)
        ######
        self.display = tk.Label(self.f, width=50, wraplength=360)
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        self.block.grid(row=0, column=0)
        s = 6
        for (i, name) in enumerate(sorted(self.buttons.keys())):
            self.buttons[name].grid(row=i%s, column=i//s)
        self.ex.grid(row=(i+1)%s, column=(i+1)//s)
        self.addexhaustion.grid(row=0, column=0)
        self.exhaustionlevel.grid(row=0, column=1)
        self.removeexhaustion.grid(row=0, column=2)
        self.display.grid(row=1, column=0)
        for name in self.character.conditions:
            try:
                self.buttons[name].config(bg='red')
            except KeyError:
                pass

    def draw_dynamic(self):
        fullconditions = '\n'.join(h.condition_defs[name]
                                   for name in self.character.conditions)
        self.display.config(text=fullconditions)
        amount = 0
        for i in range(6):
            if ('exhaustion{}'.format(i + 1) in self.character.conditions):
                amount = i + 1
                break
        colors = ['#F0F0F0', '#FFEE00', '#FFCC00', "#FF9900", "#FF6600",
                  "#FF3300", "#FF0000"]
        self.addexhaustion.config(bg=colors[amount])
        self.removeexhaustion.config(bg=colors[amount])
        self.exhaustionlevel.config(bg=colors[amount], text=str(amount))

    def toggle_condition(self, name):
        if (name in self.character.conditions):
            self.character.remove_condition(name)
            self.buttons[name].config(bg='#F0F0F0')
        else:
            self.character.add_condition(name)
            self.buttons[name].config(bg='red')
        self.draw_dynamic()

    def exhaustion(self, direction):
        if (direction == 'add'):
            self.character.add_condition('exhaustion')
        if (direction == 'remove'):
            self.character.remove_condition('exhaustion')
        # amount = 0
        # for i in range(6):
        #     if ('exhaustion{}'.format(i + 1) in self.character.conditions):
        #         amount = i + 1
        #         break
        # colors = ['#F0F0F0', '#FFEE00', '#FFCC00', "#FF9900", "#FF6600",
        #           "#FF3300", "#FF0000"]
        # self.addexhaustion.config(bg=colors[amount])
        # self.removeexhaustion.config(bg=colors[amount])
        # self.exhaustionlevel.config(bg=colors[amount], text=str(amount))
        self.draw_dynamic()


class module(ConditionsDisplay):
    def __init__(self, container, character):
        ConditionsDisplay.__init__(self, container, character)


class main(gui.Section):
    def __init__(self, window):
        gui.Section.__init__(self, window)
        self.QUIT = tk.Button(self.f, text='QUIT', command=window.destroy,
                              fg='red')
        self.startup_begin()

    def draw_static(self):
        self.core.grid(row=0, column=0)

    def startup_begin(self):
        self.charactername = {}
        gui.Query(self.charactername, self.startup_end, 'Character Name?')
        self.container.withdraw()

    def startup_end(self):
        name = self.charactername['Character Name?']
        path = 'character/' + h.clean(name) + '.character'
        if (os.path.exists(iface.JSONInterface.OBJECTSPATH + path)):
            self.record = iface.JSONInterface(path)
        else:
            gui.ErrorMessage('A character with that name was not found.')
        self.character = c.Character(self.record)
        self.core = ConditionsDisplay(self.f, self.character)
        self.draw_static()
        self.container.deiconify()


if (__name__ == '__main__'):
    win = tk.Tk()
    iface.JSONInterface.OBJECTSPATH = '../objects/'
    app = main(win)
    app.pack()
    win.mainloop()
