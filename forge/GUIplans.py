import tkinter as tk

import helpers

class Interface:
    """This presents a nested dictionary structure to the main program.
    It requires that all visible objects present a _structure variable
    that defines the pattern of frames (or other containers) within the
    object.
    It should operate like a path, with frames acting as directories.
    """
    def retrieve(root, path):
        """
        Inputs:
        Outputs:
        """
        if (not isinstance(root, dict)):
            return root
        (this, after) = path.split('/', 1)
        return retrieve(root[this], after)
        
    def makestruct(name, obj, _struct):
        """
        Frames and user-created classes are 'directories'
        Widgets (other than frames) are 'files'
        
        """
        if (isinstance(obj, tk.Frame)):
            _struct[name] = {}
            return makestruct()
        elif (isinstance(obj, Element)):
            _struct.update({name: obj._structure})
            return _struct
        elif (isinstance(obj, tk.Widget)):
            _struct.update({name: obj})
            return _struct
        else:
            return _struct
            



class Element:
    """An identifier superclass.
    All classes in this module must inherit from this.
    """
    def __init__(self, name):
        self._structure = {}
        self.__name__ = name

class Section:
    def __init__(self, container):
        self.container = container
        self.f = tk.Frame(self.container)

    def grid(self, row, column):
        self.f.grid(row=row, column=column)


class AttackResult(Section, Element):
    def __init__(self, container, attack_string, damage_string, effects):
        super().__init__(self, container)

        self.container = container
        self.attack = attack_string
        self.damage = damage_string
        self.short = helpers.shorten(effects)
        self.long = effects

    def draw(self):
        self.attack_display = tk.Label(self.f, text=attack_string)
        self.attack_display.grid(row=0, column=0)
        self.damage_display = tk.Label(self.f, text=damage_string)
        self.damage_display.grid(row=1, column=0)

        self.effect_display = EffectPane(self.f, self.short, self.long)
        self.effect_display.grid(2, 0)



class EffectPane(Section, Element):
    def __init__(self, container, short, long):
        super().__init__(self, container)

        self.short = short
        self.long = long

        self.draw()

    def draw(self):
        self.short_display = tk.Label(self.f, text=self.short)
        self.long_display = HelpButton(self.f, self.long)

        self.short_display.grid(row=0, column=0)
        self.long_display.grid(row=0, column=1)


class FeaturePane(Section, Element):
    def __init__(self, container, name, description):
        super().__init__(self, container)

        self.name = name
        self.description = description

        self.draw()

    def draw(self):
        self.stub = tk.Label(self.f, text=self.name)
        self.long_display = HelpButton(self.f, self.description)

        self.stub.grid(row=0, column=0)
        self.long_display.grid(row=0, column=1)


class HelpButton(Element):
    def __init__(self, container, poptext):
        self.container = container
        self.poptext = poptext

        self.b = tk.Button(self.container, text='?', command=lambda: self.popup())

    def popup(self):
        win = tk.TopLevel()
        disp = tk.Label(win, text=self.poptext)
        disp.grid(row=0, column=0)
        close = tk.Button(win, text='Close', command=lambda:win.destroy())
        close.grid(row=1, column=0)

    def grid(self, row, column):
        self.b.grid(row=row, column=column)
