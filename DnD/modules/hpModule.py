import tkinter as tk
from typing import Union

import dndice as d

import lib.components as gui
import lib.hpLib as hp


class HitPointDisplay(gui.Section):
    def __init__(self, container, handler: hp.HP, **kwargs):
        super().__init__(container, **kwargs)
        # self.numbers = HitPointNumberDisplay(self.f, handler)
        # self.changer = HitPointChanger(self.f, handler, self.numbers.update_view)
        self.numbers, self.changer = self._create_components(handler)
        self.draw()

    def _create_components(self, handler):
        numbers = HitPointNumberDisplay(self.f, handler)
        changer = HitPointChanger(self.f, handler, numbers.update_view)
        return numbers, changer

    def draw(self):
        self.numbers.grid(0, 0)
        self.changer.grid(1, 0)

    def on_change(self, callback: gui.Consumer):
        if self.numbers.current.callback:
            previous = self.numbers.current.callback

            def call(num):
                previous(num)
                callback(num)

            self.numbers.current.callback = call
        else:
            self.numbers.current.callback = callback


class BasicHitPointDisplay(HitPointDisplay):
    def __init__(self, container, handler: hp.HP, **kwargs):
        super().__init__(container, handler, **kwargs)

    def _create_components(self, handler):
        numbers = BaseHitPointNumberDisplay(self.f, handler)
        changer = BaseHitPointChanger(self.f, handler, numbers.update_view)
        return numbers, changer

    def draw(self):
        self.numbers.grid(0, 0)
        self.changer.grid(1, 0)


class BaseHitPointNumberDisplay(gui.Section):
    def __init__(self, container: Union[tk.BaseWidget, tk.Tk], handler: hp.HP, **kwargs):
        super().__init__(container, **kwargs)
        self.handler = handler
        self.current = gui.NumericEntry(self.f, handler.current, self.set_current, name='HP',
                                        width=5).grid(0, 0)
        tk.Label(self.f, text='/').grid(row=0, column=3, sticky='s')
        self.max = gui.NumericEntry(self.f, handler.baseMax, self.set_max, name='Max HP',
                                    width=5).grid(0, 4)

    def set_current(self, value):
        self.handler.current = value

    def set_max(self, value):
        self.handler.baseMax = value

    def update_view(self):
        self.current.set(self.handler.current)
        self.max.set(self.handler.baseMax)


class HitPointNumberDisplay(BaseHitPointNumberDisplay):
    def __init__(self, container, handler: hp.HP, **kwargs):
        super().__init__(container, handler, **kwargs)
        tk.Label(self.f, text='+').grid(row=0, column=1, sticky='s')
        self.temp = gui.NumericEntry(self.f, handler.temp, self.set_temp, name='Temp HP',
                                     width=5).grid(0, 2)
        tk.Label(self.f, text='+').grid(row=0, column=5, sticky='s')
        self.bonusMax = gui.NumericEntry(self.f, self.handler.bonusMax, self.set_bonus_max,
                                         width=5, name='Bonus Max HP').grid(0, 6)

    def set_temp(self, value):
        self.handler.temp = value

    def set_bonus_max(self, value):
        self.handler.bonusMax = value

    def update_view(self):
        self.current.set(self.handler.current)
        self.temp.set(self.handler.temp)
        self.max.set(self.handler.baseMax)
        self.bonusMax.set(self.handler.bonusMax)


class BaseHitPointChanger(gui.Section):
    def __init__(self, container: Union[tk.BaseWidget, tk.Tk], handler: hp.HP,
                 onChange: gui.Action, **kwargs):
        super().__init__(container, **kwargs)
        self.handler = handler
        self.onChange = onChange
        self.entry = tk.Entry(self.f, width=8)
        self.entry.bind('<Return>', lambda event: self.change_hp())
        self.entry.bind('<KP_Enter>', lambda event: self.change_hp())
        self.entry.grid(row=0, column=0)
        self.change = tk.Button(self.f, text='Change HP', command=self.change_hp)
        self.change.grid(row=0, column=1)
        self.amount = gui.RollDisplay(self.f)
        self.amount.grid(1, 0, columnspan=3)

    def change_hp(self):
        tree = d.compile(self.entry.get())
        value = tree.evaluate()
        self.handler.change(value)
        self.amount.set(tree)
        self.onChange()


class HitPointChanger(BaseHitPointChanger):
    def __init__(self, container, handler: hp.HP, onChange: gui.Action,
                 onTemp: gui.Action = None, **kwargs):
        super().__init__(container, handler, onChange, **kwargs)
        self.onTemp = onTemp or onChange
        self.temp = tk.Button(self.f, text='Add Temp HP', command=self.add_temp)
        self.temp.grid(row=0, column=2)

    def add_temp(self):
        tree = d.compile(self.entry.get())
        value = tree.evaluate()
        self.handler.add_temp(value)
        self.amount.set(tree)
        self.onTemp()
