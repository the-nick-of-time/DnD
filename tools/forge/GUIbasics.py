import tkinter as tk


class Element:
    """An identifier superclass.
    All classes in this module must inherit from this.
    """
    def __init__(self, name, **kwargs):
        self._structure = {}
        self.__name__ = name


class Section:
    def __init__(self, container, **kwargs):
        self.container = container
        self.f = tk.Frame(self.container)

    def grid(self, row, column):
        self.f.grid(row=row, column=column)

    def pack(self):
        self.f.pack()


class HelpButton(Element):
    def __init__(self, container, poptext):
        self.container = container
        self.poptext = poptext

        self.b = tk.Button(self.container, text='?',
                           command=lambda: self.popup())

    def popup(self):
        win = tk.Toplevel()
        disp = tk.Label(win, text=self.poptext, wraplength=250)
        disp.grid(row=0, column=0)
        close = tk.Button(win, text='Close', command=lambda: win.destroy())
        close.grid(row=1, column=0)

    def grid(self, row, column):
        self.b.grid(row=row, column=column)


class EffectPane(Section, Element):
    def __init__(self, container, short, long):
        Section.__init__(self, container)
        Element.__init__(self, 'effect')

        self.short = short
        self.long = long

        self.draw()

    def draw(self):
        self.short_display = tk.Label(self.f, text=self.short, width=30,
                                      wraplength=200)
        self.long_display = HelpButton(self.f, self.long)

        self.short_display.grid(row=0, column=0)
        self.long_display.grid(row=0, column=1)
