import tkinter as tk
from typing import Union

import lib.components as gui
import lib.resourceLib as res
import lib.settingsLib as settings


class ResourceDisplay(gui.Section):
    """Displays a resource like sorcery points or Hit Dice."""

    def __init__(self, container: Union[tk.BaseWidget, tk.Tk], resource: res.Resource,
                 lockMax=False, **kwargs):
        super().__init__(container, **kwargs)
        self.resource = resource
        self.numbers = tk.Frame(self.f)
        self.current = gui.NumericEntry(self.numbers, self.resource.number, self.set_current,
                                        width=5)
        self.max = gui.NumericEntry(self.numbers, self.resource.maxnumber, self.set_max,
                                    width=5)
        if lockMax:
            self.max.disable()
        self.value = tk.Label(self.numbers, text='*' + str(self.resource.value))
        self.buttonFrame = tk.Frame(self.f)
        self.use = tk.Button(self.buttonFrame, text='-', command=self.increment)
        self.regain = tk.Button(self.buttonFrame, text='+', command=self.decrement)
        self.display = tk.Label(self.buttonFrame, width=3)
        self.reset_ = tk.Button(self.buttonFrame, text='Reset', command=self.reset)
        self._draw()

    def _draw(self):
        tk.Label(self.f, text=self.resource.name).grid(row=0, column=0)
        self.numbers.grid(row=1, column=0)
        self.current.grid(1, 0)
        tk.Label(self.numbers, text='/').grid(row=1, column=1)
        self.max.grid(1, 2)
        self.value.grid(row=1, column=4)
        self.buttonFrame.grid(row=2, column=0, columnspan=3)
        self.display.grid(row=0, column=0)
        self.regain.grid(row=0, column=1)
        self.use.grid(row=0, column=2)
        self.reset_.grid(row=0, column=3)

    def update_view(self):
        self.max.set(self.resource.maxnumber)
        self.current.set(self.resource.number)

    def set_current(self, value):
        self.resource.number = value

    def set_max(self, value):
        self.resource.maxnumber = value

    def increment(self):
        self.resource.regain(1)
        self.update_view()

    def decrement(self):
        val = self.resource.use(1)
        self.display.config(text=str(val))
        self.update_view()

    def reset(self):
        self.resource.reset()
        self.update_view()

    def rest(self, which: settings.RestLength):
        self.resource.rest(which)
        self.update_view()
