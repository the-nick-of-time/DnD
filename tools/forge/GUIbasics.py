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
        self.f = tk.Frame(self.container, **kwargs)

    def grid(self, row, column, **kwargs):
        self.f.grid(row=row, column=column, **kwargs)

    def pack(self):
        self.f.pack()

    # def data_dump(self):
    #     raise NotImplementedError


class InfoButton:
    def __init__(self, container, poptext):
        self.container = container
        self.poptext = poptext

        self.b = tk.Button(self.container, text='?', command=self.popup)

    def popup(self):
        win = tk.Toplevel()
        disp = tk.Label(win, text=self.poptext, wraplength=250)
        disp.grid(row=0, column=0)
        close = tk.Button(win, text='Close', command=win.destroy)
        close.grid(row=1, column=0)

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

        self.draw()

    def __bool__(self):
        return bool(self.short or self.long)

    def draw(self):
        self.short_display = tk.Label(self.f, text=self.short, width=30,
                                      wraplength=200)
        self.long_display = InfoButton(self.f, self.long)

        self.short_display.grid(row=0, column=0)
        self.long_display.grid(row=0, column=1)


class Query:
    def __init__(self, data, *questions):
        """questions is made of strings that will label the entries and identify outputs
        data is an empty dictionary"""
        self.data = data
        self.questions = questions
        self.answers = {}
        self.win = tk.Toplevel()
        self.accept = tk.Button(subwin, text='Accept', command=self.finish)
        self.draw()

    def draw(self):
        for (i, q) in enumerate(self.questions):
            self.answers[q] = util.labeledEntry(subwin, q, 2*i, 0)
        self.accept.grid(row=2*i+1, column=1)

    def finish(self):
        for q in self.questions:
            self.data.update({q: self.answers[q].get()})
        self.win.destroy()


class ResourceDisplay(Section):
    def __init__(self, container, resource):
        Section.__init__(self, container)
        self.resource = resource
        self.name = tk.Label(self.f, text=self.resource.name)
        self.numbers = tk.Frame(self.f)
        self.currentvalue = tk.StringVar()
        self.currentvalue.trace('w', lambda a,b,c: self.update_number())
        self.current = tk.Entry(self.numbers, textvariable=self.currentvalue,
                                width=5)
        self.slash = tk.Label(self.numbers, text='/')
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
        self.inc.grid(row=0, column=0)
        self.dec.grid(row=0, column=1)
        self.resetbutton.grid(row=0, column=2)

    def draw_dynamic(self):
        # might need string conversion
        self.mxvalue.set(str(self.resource.maxnumber))
        self.currentvalue.set(str(self.resource.number))

    def update_number(self):
        self.resource.number = int(self.currentvalue.get() or 0)

    def update_maxnumber(self):
        self.resource.maxnumber = int(self.mxvalue.get() or 0)

    def increment(self):
        self.resource.regain(1)
        self.draw_dynamic()

    def decrement(self):
        self.resource.use(1)
        self.draw_dynamic()

    def reset(self):
        self.resource.reset()
        self.draw_dynamic()


# class ItemDisplay(Section):
#     def __init__(self, container, item):
#         Section.__init__(self, container)
#         self.item = item
#         self.name = tk.Label(self.f, text=self.item.name)
#         self.numbers = tk.Label(self.f)
#         self.buttonframe = tk.Frame(self.f)
#         self.use = tk.Button(self.buttonframe, text='+',
#                              command=lambda: )
#         self.dec = tk.Button(self.buttonframe, text='-',
#                              command=lambda: )
#         self.resetbutton = tk.Button(self.buttonframe, text='-',
#                                command=lambda: self.resource.reset())
#         self.draw_static()
#         self.draw_dynamic()
#
#     def draw_static(self):
#         self.name.grid(row=0, column=0)
#         self.numbers.grid(row=1, column=0)
#         self.buttonframe.grid(row=2, column=0)
#         self.inc.grid(row=0, column=0)
#         self.dec.grid(row=0, column=1)
#         self.resetbutton.grid(row=0, column=2)
#
#     def draw_dynamic(self):
#         if (isinstance(self.resource.value, str)):
#             numbers['text'] = '{num}/{max} ({val})'.format(
#                 num=self.resource.number, max=self.resource.maxnumber,
#                 val=self.resource.value)
#         else:
#             numbers['text'] = '{num}/{max}'.format(
#                 num=self.resource.number, max=self.resource.maxnumber)
#         # self.numbers.grid(row=1, column=0)  # not sure if this is necessary
#
#     def increment(self):
#         self.resource.regain(1)
#         self.draw_dynamic()
#
#     def decrement(self):
#         self.resource.use(1)
#         self.draw_dynamic()
