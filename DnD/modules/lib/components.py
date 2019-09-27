import enum
import tkinter as tk
from pathlib import Path
from typing import Callable, Any, Optional, Union

import dndice as d

from . import characterLib as char
from . import exceptionsLib as ex
from . import helpers as h
from . import interface as iface

Action = Callable[[], None]
EventHandler = Callable[[tk.Event], None]
Consumer = Callable[[Any], None]
Initializer = Callable[[tk.Widget], 'Section']


class Direction(enum.Enum):
    VERTICAL = V = 'vertical'
    HORIZONTAL = H = 'horizontal'


class Section:
    """A placeable collection of widgets, that can have a scrollbar.
    From the outside it acts like a frame, as its central portion is a frame.
    """

    def __init__(self, container: Union[tk.BaseWidget, tk.Tk], **kwargs):
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
        if hasattr(self, 'wrapper'):
            self.wrapper.grid(row=row, column=column, **kwargs)
            self.canvas.grid(row=0, column=0)
            self.vscroll.grid(row=0, column=1, sticky='ns')
            self.hscroll.grid(row=1, column=0, sticky='ew')
            self.canvas.create_window((0, 0), window=self.f, anchor='nw')
            self.f.bind("<Configure>", lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        else:
            self.f.grid(row=row, column=column, **kwargs)
        return self

    def pack(self, **kwargs):
        if hasattr(self, 'wrapper'):
            self.wrapper.pack(**kwargs)
            self.canvas.grid(row=0, column=0)
            self.vscroll.grid(row=0, column=1, sticky='ns')
            self.hscroll.grid(row=1, column=0, sticky='ew')
            self.canvas.create_window((0, 0), window=self.f, anchor='nw')
            self.f.bind("<Configure>", lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))
        else:
            self.f.pack(**kwargs)
        return self

    def destroy(self):
        if hasattr(self, 'wrapper'):
            self.wrapper.destroy()
        else:
            self.f.destroy()

    def all_children(self):
        """Iterate over everything contained in this Section."""
        # Should this select `wrapper` if present? that would capture scroll bars, etc.
        yield from self.__all_children_recursive(self.f)

    def __all_children_recursive(self, current: tk.BaseWidget):
        yield current
        for child in current.winfo_children():
            yield from self.__all_children_recursive(child)


class DynamicGrid:
    """A collection of widgets which will wrap automatically."""

    def __init__(self, container):
        self.f = tk.Frame(container)
        self.scrollbar = tk.Scrollbar(self.f)
        self.container = tk.Text(self.f, wrap="char", borderwidth=0, highlightthickness=0,
                                 state="disabled", background=self.f["background"],
                                 cursor='arrow', yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(self.container.yview)
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.container.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    def add(self, creator: Initializer, index='end') -> Section:
        """Add a component to the grid.

        :param creator: A callable that takes one argument, the
            container, and returns the component bound into that
            container.
        :param index: Either a number or 'end'; where to insert the new
            component
        :return: The created component.
        """
        component = creator(self.container)
        self.container['state'] = 'normal'
        self.container.window_create(index, window=component)
        self.container['state'] = 'disabled'
        return component

    def remove(self, component):
        """Remove a component from the grid.

        :param component: The component to delete, as returned from
            `add`.
        """
        self.container['state'] = 'normal'
        self.container.delete(component)
        self.container['state'] = 'disabled'

    def grid(self, row, column, **kwargs):
        self.f.grid(row=row, column=column, **kwargs)
        return self

    def pack(self, **kwargs):
        self.f.pack(**kwargs)
        return self


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
        return self


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


class ProficientButton(tk.Button):
    """A button which shows whether you are proficient in an action."""

    def __init__(self, container, name: str, proficient: bool = False, **kw):
        super().__init__(container, **kw)
        self.defaultColor = self.cget('bg')
        self.name = name
        self['text'] = name
        self.proficient = proficient

    def __setattr__(self, key, value):
        if key == 'proficient':
            # Update color
            if value:
                self.config(background='green', foreground='white')
            else:
                self.config(background=self.defaultColor, foreground='black')
        super().__setattr__(key, value)

    def grid(self, row, column, **kwargs):
        super().grid(row=row, column=column, **kwargs)
        return self


class EffectPane(Section):
    """Has a short label and an InfoButton with the full text."""

    def __init__(self, container, short: str, long: str):
        Section.__init__(self, container)

        self.short = short
        self.long = long

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
        self.draw_dynamic()


class Query:
    """Asks a series of questions of the user and uses the callback to
    return the data.
    """

    def __init__(self, callbackfun: Callable[[dict], None], *questions):
        """Ask a series of questions of the user.

        :param callbackfun: The function to call with the entered data
            when done
        :param questions: The list of questions to ask, either strings
            or 2-tuples with (question, [list of options])
        """
        self.callback = callbackfun
        self.questions = questions
        self.answers = {}
        self.win = tk.Toplevel()
        self.accept = tk.Button(self.win, text='Accept', command=self.finish)
        self.draw()

    def draw(self):
        """Create and place the widgets."""
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
        self.accept.grid(row=i + 1, column=1)

    def finish(self):
        """Call the callback function to give data back."""
        data = {}
        for q in self.questions:
            if isinstance(q, str):
                data.update({q: self.answers[q].get()})
            else:
                data.update({q[0]: self.answers[q[0]].get()})
        self.callback(data)
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
        self.value = tk.Label(self.numbers,
                              text='*' + v if isinstance(v, str) else '')
        self.buttonFrame = tk.Frame(self.f)
        self.inc = tk.Button(self.buttonFrame, text='+',
                             command=self.increment)
        self.dec = tk.Button(self.buttonFrame, text='-',
                             command=self.decrement)
        self.resetbutton = tk.Button(self.buttonFrame, text='Reset',
                                     command=self.reset)
        self.display = tk.Label(self.buttonFrame, width=3)
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        self.name.grid(row=0, column=0)
        self.numbers.grid(row=1, column=0)
        self.current.grid(row=0, column=0)
        self.slash.grid(row=0, column=1)
        self.mx.grid(row=0, column=2)
        self.value.grid(row=0, column=3)
        self.buttonFrame.grid(row=2, column=0)
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
    NAME_Q = 'Character Name?'

    def __init__(self, callbackfun: Callable[[dict], None], *extraQuestions):
        possibilities = []
        base = iface.JsonInterface.OBJECTSPATH / 'character'
        for f in base.glob('*.character'):
            possibilities.append(h.readable_filename(f.stem))
        Query.__init__(self, callbackfun,
                       [self.NAME_Q, sorted(possibilities)],
                       *extraQuestions)


class LabeledEntry(Section):
    def __init__(self, parent, name, orient=Direction.VERTICAL, width=20, pos=''):
        super().__init__(parent)
        self.label = tk.Label(self.f, text=name)
        self.label.grid(row=0, column=0, sticky=pos)
        self.value = tk.StringVar()
        self.entry = tk.Entry(self.f, textvariable=self.value, width=width)
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

    def bind(self, event: str, callback: EventHandler):
        self.entry.bind(event, callback)

    def on_change(self, callback: Action):
        # Ignore everything that the trace argument gives
        self.value.trace_add('write', lambda name, index, op: callback())

    def get(self):
        return self.entry.get()


class LabeledMenu(Section):
    def __init__(self, parent, name, values, orient=Direction.VERTICAL):
        super().__init__(parent)
        self.label = tk.Label(self.f, text=name)
        self.label.grid(row=0, column=0)
        self.value = tk.StringVar()
        self.menu = tk.OptionMenu(self.f, self.value, *values)
        if orient == Direction.VERTICAL:
            self.menu.grid(row=1, column=0)
        elif orient == Direction.HORIZONTAL:
            self.menu.grid(row=0, column=1)
        else:
            raise ex.GuiError("Pass in a Direction value")

    def get(self):
        return self.value.get()

    def focus(self):
        self.menu.focus_set()

    def bind(self, event, callback):
        self.menu.bind(event, callback)


# This and Counter could be replaced with ttk.Spinbox?
class NumericEntry(Section):
    """An entry that only accepts integer values."""
    def __init__(self, container, start: int = 0, callback: Optional[Consumer] = None,
                 width=20, name='', orient=Direction.VERTICAL):
        super().__init__(container)
        if name:
            self.label = tk.Label(self.f, text=name)
        else:
            self.label = None
        self.value = tk.StringVar()
        self.value.set(str(start))
        self.entry = tk.Entry(self.f, width=width, textvariable=self.value)
        validate = (self.entry.register(self.__try_update), '%P')
        self.entry['validate'] = 'key'
        self.entry['validatecommand'] = validate
        self.callback = callback
        self._draw(orient)

    def __try_update(self, value: str):
        try:
            num = int(value)
            if self.callback:
                self.callback(num)
            return True
        except ValueError:
            return False

    def _draw(self, orient):
        self.label.grid(row=0, column=0)
        if orient == Direction.V:
            self.entry.grid(row=1, column=0)
        else:
            self.entry.grid(row=0, column=1)

    def get(self):
        return int(self.value.get() or 0)

    def set(self, value: int):
        self.value.set(str(value))

    def clear(self):
        self.value.set('0')

    def focus(self):
        self.entry.focus_set()

    def bind(self, event: str, callback: EventHandler):
        self.entry.bind(event, callback)


class Counter(NumericEntry):
    """A number entry with + and - buttons to change the number."""

    def __init__(self, container, start: int = 0, callback: Optional[Consumer] = None, name=''):
        super().__init__(container, start, callback, width=5, name=name)
        self.minus = tk.Button(self.f, text='-', command=lambda: self.change(-1))
        self.plus = tk.Button(self.f, text='+', command=lambda: self.change(1))

    def _draw(self, orient):
        self.label.grid(row=0, column=1, columnspan=3)
        self.minus.grid(row=1, column=0)
        self.entry.grid(row=1, column=1)
        self.plus.grid(row=1, column=2)

    def change(self, number: int):
        self.set(self.get() + number)


class AdvantageChooser(Section):
    """Select advantage and disadvantage, and get the matching d20 roll."""
    def __init__(self, container, orient=Direction.VERTICAL, **kwargs):
        super().__init__(container, **kwargs)
        self._adv = tk.BooleanVar()
        self._dis = tk.BooleanVar()
        advantageSelect = tk.Checkbutton(self.f, text="Advantage?",
                                         variable=self._adv)
        disadvantageSelect = tk.Checkbutton(self.f, text="Disadvantage?",
                                            variable=self._dis)
        advantageSelect.grid(row=0, column=0)
        if orient == Direction.V:
            disadvantageSelect.grid(row=1, column=0)
        elif orient == Direction.HORIZONTAL:
            disadvantageSelect.grid(row=0, column=1)
        else:
            raise ex.GuiError("Pass in a Direction value")

    def d20_roll(self, lucky=False):
        """Return the correct d20 roll to make given the advantage"""
        return h.d20_roll(self._adv.get(), self._dis.get(), lucky)

    @property
    def advantage(self) -> bool:
        return self._adv.get()

    @property
    def disadvantage(self) -> bool:
        return self._dis.get()


class FreeformAttack(Section):
    """Allow arbitrary attack modifiers and damage roll"""

    def __init__(self, container, attackResult: 'RollDisplay' = None,
                 damageResult: 'RollDisplay' = None, **kwargs):
        super().__init__(container, **kwargs)
        self.attack = LabeledEntry(self.f, 'Attack Modifiers', orient=Direction.HORIZONTAL,
                                   width=10)
        self.damage = LabeledEntry(self.f, 'Damage Roll', orient=Direction.HORIZONTAL, width=10)
        self.adv = AdvantageChooser(self.f)
        self.doAttack = tk.Button(self.f, command=self.do_attack, text='Perform attack')
        self.attackResult = attackResult or RollDisplay(self.f)
        self.damageResult = damageResult or RollDisplay(self.f)
        self.attack.grid(0, 0)
        self.adv.grid(0, 1)
        self.damage.grid(1, 0)
        self.doAttack.grid(row=1, column=1)
        self.attackResult.grid(2, 0, columnspan=2)
        self.damageResult.grid(3, 0, columnspan=2)

    def do_attack(self, lucky=False):
        attack = self.adv.d20_roll(lucky)
        attack += d.compile(self.attack.get())
        att = d.verbose(attack)
        if attack.is_critical():
            att = 'Critical Hit'
            dam = d.verbose(self.damage.get(), d.Mode.CRIT)
        elif attack.is_fail():
            att = 'Critical Miss'
            dam = '0'
        else:
            dam = d.verbose(self.damage.get())
        self.attackResult['text'] = 'Attack roll: ' + att
        self.damageResult['text'] = 'Damage roll: ' + dam


class RollDisplay(Section):
    """Displays a roll, color-coded to indicate if it's a critical hit."""
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        self.display = tk.Label(self.f)
        self.display.grid(row=0, column=0)

    def set(self, expr: d.core.EvalTree):
        """Display the given expression."""
        text = expr.verbose_result()
        if expr.is_critical():
            color = 'green'
        elif expr.is_fail():
            color = 'red'
        else:
            color = 'black'
        self.display['text'] = text
        self.display['foreground'] = color

    def clear(self):
        """Clear the text field."""
        self.display['text'] = ''


class MainWindow(tk.Tk):
    """The main window, with the className set to play nice for taskbar merging."""
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs, className='dndutils')
        self.title('D&D')


class MainModule:
    """When a module is being called as the main program, invoke this.

    Asks for the character name and loads it before creating the actual
    component using the given function.
    """
    def __init__(self, window: tk.Tk, creator: 'Callable[[char.Character], Section]'):
        self.window = window
        self.creator = creator
        self.component = None
        objects = (Path(__file__).parent / '..' / '..' / 'objects').resolve()
        iface.JsonInterface.OBJECTSPATH = objects
        self.QUIT = tk.Button(self.window, text='QUIT', fg='red', command=self.quit)
        self.QUIT.grid(row=10, column=0)

        self.startup_begin()

    def startup_begin(self):
        """Ask for the character name and wait for response."""
        CharacterQuery(self.startup_end)
        self.window.withdraw()

    def startup_end(self, data):
        """Instantiate the selected character and create the component."""
        try:
            name = data[CharacterQuery.NAME_Q]
            path = (iface.JsonInterface.OBJECTSPATH
                    / 'character' / (h.sanitize_filename(name) + '.character'))
            if path.exists():
                jf = iface.JsonInterface(path, isabsolute=True)
            else:
                # Should be unreachable since the list of names is
                # determined by files that exist
                raise FileNotFoundError("The named character doesn't exist")
            character = char.Character(jf)
            self.component = self.creator(character)

            self.component.grid(0, 0)
            self.window.deiconify()
        except Exception:
            # Otherwise it would continue running in the background,
            # unable to be killed because it's hidden
            self.window.destroy()
            raise

    def run(self):
        """Run the application."""
        self.window.mainloop()

    def quit(self):
        """Ensure that the character data is written and quit."""
        if hasattr(self.component, 'owner'):
            # noinspection PyUnresolvedReferences
            self.component.owner.write()
        self.window.destroy()
