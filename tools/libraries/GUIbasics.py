import tkinter as tk
# import tools.libraries.tkUtility as util
import tkUtility as util


class Element:
    def draw_static(self):
        raise NotImplementedError

    def draw_dynamic(self):
        raise NotImplementedError


class Section:
    def __init__(self, container, **kwargs):
        self.container = container
        if ('height' in kwargs or 'width' in kwargs):
            # only intended for use with both arguments currently
            # might separate into defined height -> vertical scroll, defined width -> horizontal scroll
            self.wrapper = tk.Frame(self.container, **kwargs)
            self.canvas = tk.Canvas(self.wrapper, bd=0,
                                    height=kwargs.get('height', 0),
                                    width=kwargs.get('width', 0))
            self.vscroll = tk.Scrollbar(self.wrapper, orient='vertical', command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.vscroll.set)
            self.hscroll = tk.Scrollbar(self.wrapper, orient='horizontal', command=self.canvas.xview)
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
        except AttributeError as e:
            self.f.pack(**kwargs)


class InfoButton:
    def __init__(self, container, poptext, title=''):
        self.container = container
        self.poptext = poptext
        self.title = title

        self.b = tk.Button(self.container, text='?', command=self.popup)

    def popup(self):
        win = tk.Toplevel()
        if (self.title):
            win.title(self.title)
        disp = tk.Label(win, text=self.poptext, wraplength=250)
        # if (isinstance(self.poptext, tk.StringVar)):
        #     disp['textvariable'] = self.poptext
        # elif (isinstance(self.poptext, str)):
        #     disp['text'] = self.poptext
        disp.grid(row=0, column=0)
        close = tk.Button(win, text='Close', command=win.destroy)
        close.grid(row=1, column=0)

    def update(self, poptext):
        self.poptext = poptext

    def grid(self, row, column):
        self.b.grid(row=row, column=column)


class ErrorMessage:
    def __init__(self, message):
        self.win = tk.Toplevel()
        tell = tk.Label(self.win, text=message)
        tell.pack()
        close = tk.Button(self.win, text='OK', command=self.win.destroy)
        close.pack()


class EffectPane(Section):
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
    def __init__(self, data, callbackfun, *questions):
        """questions is made of strings that will label the entries and identify outputs
        data is an empty dictionary"""
        self.data = data
        self.callback = callbackfun
        self.questions = questions
        self.answers = {}
        self.win = tk.Toplevel()
        self.accept = tk.Button(self.win, text='Accept', command=self.finish)
        self.draw()

    def draw(self):
        for (i, q) in enumerate(self.questions):
            self.answers[q] = util.labeledEntry(self.win, q, 2*i, 0)
        self.answers[self.questions[-1]].bind("<Return>",
                                              lambda event: self.finish())
        self.answers[self.questions[0]].focus_set()
        self.accept.grid(row=2*i+1, column=1)

    def finish(self):
        for q in self.questions:
            self.data.update({q: self.answers[q].get()})
        self.callback()
        self.win.destroy()


class ResourceDisplay(Section):
    def __init__(self, container, resource, lockMax=False):
        Section.__init__(self, container)
        self.resource = resource
        self.lockMax = lockMax
        self.name = tk.Label(self.f, text=self.resource.name)
        self.numbers = tk.Frame(self.f)
        self.currentvalue = tk.StringVar()
        self.currentvalue.trace('w', lambda a,b,c: self.update_number())
        self.current = tk.Entry(self.numbers, textvariable=self.currentvalue,
                                width=5)
        self.slash = tk.Label(self.numbers, text='/')
        if (lockMax):
            self.mx = tk.Label(self.numbers, width=5,
                               text=str(self.resource.maxnumber))
        else:
            self.mxvalue = tk.StringVar()
            self.mxvalue.trace('w', lambda a,b,c: self.update_maxnumber())
            self.mx = tk.Entry(self.numbers, textvariable=self.mxvalue, width=5)
        self.value = tk.Label(self.numbers, text='*'+self.resource.value if isinstance(self.resource.value, str) else '')
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
        if (not self.lockMax):
            self.mxvalue.set(str(self.resource.maxnumber))
        self.currentvalue.set(str(self.resource.number))

    def update_number(self):
        val = self.currentvalue.get()
        if (val.isnumeric()):
            self.resource.number = int(val)

    def update_maxnumber(self):
        self.resource.maxnumber = int(self.mxvalue.get() or 0)

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
