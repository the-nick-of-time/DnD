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
    def __init__(self, question):
        self.draw()
        self.question = question

    def draw(self):
        self.win = tk.Toplevel()
        self.answer = util.labeledEntry(subwin, self.question, 0, 0)
        self.accept = tk.Button(subwin, text='Accept', command=self.finish)
        self.accept.grid(row=1, column=1)

    def finish(self):
        answer = self.answer.get()
        self.win.destroy()
        return answer
        # Somehow needs to actually communicate with its caller


class ResourceDisplay(Section):
    def __init__(self, container, resource):
        Section.__init__(self, container)
        self.resource = resource
        self.name = tk.Label(self.f, text=self.resource.name)
        self.numbers = tk.Label(self.f)
        self.buttonframe = tk.Frame(self.f)
        self.inc = tk.Button(self.buttonframe, text='+',
                             command=self.increment)
        self.dec = tk.Button(self.buttonframe, text='-',
                             command=self.decrement)
        self.resetbutton = tk.Button(self.buttonframe, text='-',
                               command=self.reset)
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        self.name.grid(row=0, column=0)
        self.numbers.grid(row=1, column=0)
        self.buttonframe.grid(row=2, column=0)
        self.inc.grid(row=0, column=0)
        self.dec.grid(row=0, column=1)
        self.resetbutton.grid(row=0, column=2)

    def draw_dynamic(self):
        if (isinstance(self.resource.value, str)):
            numbers['text'] = '{num}/{max} ({val})'.format(
                num=self.resource.number, max=self.resource.maxnumber,
                val=self.resource.value)
        else:
            numbers['text'] = '{num}/{max}'.format(
                num=self.resource.number, max=self.resource.maxnumber)
        # self.numbers.grid(row=1, column=0)  # not sure if this is necessary

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
