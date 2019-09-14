import enum
import sys
import tkinter as tk
from os.path import abspath, dirname

sys.path.insert(0, dirname(abspath(__file__)))


class Direction(enum.Enum):
    V = 'vertical'
    VERTICAL = 'vertical'
    H = 'horizontal'
    HORIZONTAL = 'horizontal'


class Section:
    """A placeable collection of widgets, that can have a scrollbar.
    From the outside it acts like a frame, as its central portion is a frame
    """

    def __init__(self, container, **kwargs):
        self.container = container
        if 'height' in kwargs or 'width' in kwargs:
            # only intended for use with both arguments currently
            # might separate into defined height -> vertical scroll, defined
            #   width -> horizontal scroll
            self.wrapper = tk.Frame(self.container, **kwargs)
            self.canvas = tk.Canvas(self.wrapper, bd=0,
                                    height=kwargs.get('height', 0),
                                    width=kwargs.get('width', 0))
            self.vscroll = tk.Scrollbar(self.wrapper, orient='vertical',
                                        command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.vscroll.set)
            self.hscroll = tk.Scrollbar(self.wrapper, orient='horizontal',
                                        command=self.canvas.xview)
            self.canvas.configure(xscrollcommand=self.hscroll.set)
            # Probably use self.canvas.create_window() to place f
            self.f = tk.Frame(self.canvas, **kwargs)
        else:
            self.f = tk.Frame(self.container, **kwargs)

    def grid(self, row, column, **kwargs):
        try:
            self.wrapper.grid(row=row, column=column, **kwargs)
            self.canvas.grid(row=0, column=0)
            self.vscroll.grid(row=0, column=1, sticky='ns')
            self.hscroll.grid(row=1, column=0, sticky='ew')
            self.canvas.create_window((0, 0), window=self.f, anchor='nw')
            self.f.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        except AttributeError:
            self.f.grid(row=row, column=column, **kwargs)

    def pack(self, **kwargs):
        try:
            self.wrapper.pack(**kwargs)
            self.canvas.grid(row=0, column=0)
            self.vscroll.grid(row=0, column=1, sticky='ns')
            self.hscroll.grid(row=1, column=0, sticky='ew')
            self.canvas.create_window((0, 0), window=self.f, anchor='nw')
            self.f.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        except AttributeError:
            self.f.pack(**kwargs)

    def destroy(self):
        try:
            self.wrapper.destroy()
        except AttributeError:
            self.f.destroy()


class InfoButton:
    """A small button that spawns a popup window with detailed information."""

    def __init__(self, container, poptext, title=''):
        self.container = container
        self.poptext = poptext
        self.title = title

        self.b = tk.Button(self.container, text='?', command=self.popup)

    def popup(self):
        win = tk.Toplevel()
        if self.title:
            win.title(self.title)
        disp = tk.Label(win, text=self.poptext, wraplength=250)
        disp.grid(row=0, column=0)
        close = tk.Button(win, text='Close', command=win.destroy)
        close.grid(row=1, column=0)

    def update(self, poptext):
        self.poptext = poptext

    def grid(self, row, column):
        self.b.grid(row=row, column=column)


class ErrorMessage:
    """An error message popup.
    Maybe replaceable with tk.messageBox.showerror
    """

    def __init__(self, message):
        self.win = tk.Toplevel()
        tell = tk.Label(self.win, text=message)
        tell.pack()
        close = tk.Button(self.win, text='OK', command=self.win.destroy)
        close.pack()


class EffectPane(Section):
    """Has a short label and an InfoButton with the full text.
    """

    def __init__(self, container, short, long):
        Section.__init__(self, container)

        self.short = short
        self.long = long
        # self.short = tk.StringVar(value=short)
        # self.long = tk.StringVar(value=long)

        self.short_display = tk.Label(self.f, text=self.short, width=30,
                                      wraplength=200)
        self.long_display = InfoButton(self.f, self.long, self.short)

        self.draw_static()
        self.draw_dynamic()

    def __bool__(self):
        return bool(self.short or self.long)

    def draw_static(self):
        self.short_display.grid(row=0, column=0)
        self.long_display.grid(row=0, column=1)

    def draw_dynamic(self):
        self.short_display['text'] = self.short
        self.long_display.update(self.long)

    def update(self, short, long):
        self.short = short
        self.long = long
        # self.long_display.poptext = long
        # self.short = tk.StringVar(value=short)
        # self.long = tk.StringVar(value=long)
        self.draw_dynamic()


class Query:
    """Asks a series of questions of the user and writes into a given dict."""

    def __init__(self, data, callbackfun, *questions):
        """Ask a series of questions of the user.
        questions is made of strings that will label the entries and identify
            outputs
        data is an empty dictionary"""
        # TODO: make callbackfun take one argument so it can take the data and remove the data parameter
        self.data = data
        self.callback = callbackfun
        self.questions = questions
        self.answers = {}
        self.win = tk.Toplevel()
        self.accept = tk.Button(self.win, text='Accept', command=self.finish)
        self.draw()

    def draw(self):
        i = 0
        for i, q in enumerate(self.questions):
            if isinstance(q, (list, tuple)) and len(q) == 2:
                # an explicit list of options
                menu = LabeledMenu(self.win, q[0], q[1])
                self.answers[q[0]] = menu
                menu.grid(i, 0)
            elif isinstance(q, str):
                entry = LabeledEntry(self.win, q)
                self.answers[q] = entry
                entry.grid(i, 0)
        lastname = (self.questions[-1] if isinstance(self.questions[-1], str)
                    else self.questions[-1][0])
        firstname = (self.questions[0] if isinstance(self.questions[0], str)
                     else self.questions[0][0])
        self.answers[firstname].focus()
        self.answers[lastname].bind("<Return>", lambda e: self.finish())
        self.accept.grid(row=i+1, column=1)

    def finish(self):
        for q in self.questions:
            if isinstance(q, str):
                self.data.update({q: self.answers[q].get()})
            else:
                self.data.update({q[0]: self.answers[q[0]].get()})
        self.callback()
        self.win.destroy()


class ResourceDisplay(Section):
    """Displays a resource like sorcery points or Hit Dice."""

    def __init__(self, container, resource, lockMax=False):
        Section.__init__(self, container)
        self.resource = resource
        self.lockMax = lockMax
        self.name = tk.Label(self.f, text=self.resource.name)
        self.numbers = tk.Frame(self.f)
        self.currentvalue = tk.StringVar()
        self.currentvalue.trace('w', lambda a, b, c: self.update_number())
        self.current = tk.Entry(self.numbers, textvariable=self.currentvalue,
                                width=5)
        self.slash = tk.Label(self.numbers, text='/')
        if lockMax:
            self.mx = tk.Label(self.numbers, width=5,
                               text=str(self.resource.maxnumber))
        else:
            self.maxvalue = tk.StringVar()
            self.maxvalue.trace('w', lambda a, b, c: self.update_maxnumber())
            self.mx = tk.Entry(self.numbers, textvariable=self.maxvalue,
                               width=5)
        v = self.resource.value
        self.value = tk.Label(self.numbers, text='*' + v if isinstance(v, str)
                              else '')
        self.buttonframe = tk.Frame(self.f)
        self.inc = tk.Button(self.buttonframe, text='+',
                             command=self.increment)
        self.dec = tk.Button(self.buttonframe, text='-',
                             command=self.decrement)
        self.resetbutton = tk.Button(self.buttonframe, text='Reset',
                                     command=self.reset)
        self.display = tk.Label(self.buttonframe, width=3)
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        self.name.grid(row=0, column=0)
        self.numbers.grid(row=1, column=0)
        self.current.grid(row=0, column=0)
        self.slash.grid(row=0, column=1)
        self.mx.grid(row=0, column=2)
        self.value.grid(row=0, column=3)
        self.buttonframe.grid(row=2, column=0)
        self.display.grid(row=0, column=0)
        self.inc.grid(row=0, column=1)
        self.dec.grid(row=0, column=2)
        self.resetbutton.grid(row=0, column=3)

    def draw_dynamic(self):
        if not self.lockMax:
            self.maxvalue.set(str(self.resource.maxnumber))
        self.currentvalue.set(str(self.resource.number))

    def update_number(self):
        val = self.currentvalue.get()
        if val.isnumeric():
            self.resource.number = int(val)

    def update_maxnumber(self):
        self.resource.maxnumber = int(self.maxvalue.get() or 0)

    def increment(self):
        self.resource.regain(1)
        self.draw_dynamic()

    def decrement(self):
        val = self.resource.use(1)
        self.display.config(text=str(val))
        self.draw_dynamic()

    def reset(self):
        self.resource.reset()
        self.draw_dynamic()

    def rest(self, which):
        self.resource.rest(which)
        self.draw_dynamic()


class AskLine(Section):
    """Displays a labeled data entry box with a descriptor InfoButton.
    Methods:
    get: Get the data from the entry widget.
    """

    def __init__(self, container, name, description, widgetmaker, puller=None):
        # widgetmaker is a function that takes one argument, the widget's
        #   master, and returns the widget
        # puller is either None, which makes the puller the widget's .get()
        #   method, or a function that takes the widget as its only argument
        #   and returns the data from it
        Section.__init__(self, container)
        self.nameL = tk.Label(self.f, text=name)
        self.widget = widgetmaker(self.f)
        if description:
            self.describer = InfoButton(self.f, description, name)
        else:
            # Have a zero-size widget as a dummy
            self.describer = tk.Label(self.f)
        if puller is not None:
            self.puller = lambda: puller(self.widget)
        else:
            self.puller = self.widget.get
        self.draw_static()

    def draw_static(self):
        self.nameL.grid(row=0, column=0)
        self.widget.grid(row=0, column=1)
        self.describer.grid(row=0, column=2)

    def get(self):
        return self.puller()


class CharacterQuery(Query):
    def __init__(self, data, callbackfun, *extraquestions):
        import os
        import interface as iface
        import re
        import helpers as h
        possibilities = []
        for f in os.scandir(iface.JSONInterface.OBJECTSPATH + 'character'):
            m = re.match(r'(.*)\.character', f.name)
            name = m.group(1)
            possibilities.append(h.unclean(name))
        Query.__init__(self, data, callbackfun,
                       ['Character Name?', sorted(possibilities)],
                       *extraquestions)


class LabeledEntry(Section):
    def __init__(self, parent, name, orient=Direction.VERTICAL, width=20, pos=''):
        super().__init__(parent)
        self.label = tk.Label(self.f, text=name)
        self.label.grid(row=0, column=0)
        self.entry = tk.Entry(self.f, width=width)
        if orient == Direction.VERTICAL:
            self.entry.grid(row=1, column=0, sticky=pos)
        elif orient == Direction.HORIZONTAL:
            self.entry.grid(row=0, column=1, sticky=pos)

    def relabel(self, label):
        self.label['text'] = label

    def clear(self):
        self.entry.delete(0, 'end')

    def replace_text(self, new):
        self.clear()
        self.entry.insert(0, new)

    def focus(self):
        self.entry.focus_set()

    def bind(self, event, callback):
        self.entry.bind(event, callback)

    def get(self):
        return self.entry.get()


class LabeledMenu(Section):
    def __init__(self, parent, name, values, orient=Direction.VERTICAL):
        super().__init__(parent)
        self.label = tk.Label(self.f, text=name)
        self.label.grid(row=0, column=0)
        self.value = tk.StringVar()
        self.menu = tk.OptionMenu(self.f, self.value, name, *values)
        if orient == Direction.VERTICAL:
            self.menu.grid(row=1, column=0)
        elif orient == Direction.HORIZONTAL:
            self.menu.grid(row=0, column=1)

    def get(self):
        return self.value.get()

    def focus(self):
        self.menu.focus_set()

    def bind(self, event, callback):
        self.menu.bind(event, callback)


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs, className='dndutils')
