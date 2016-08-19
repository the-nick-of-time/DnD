import tools.forge.helpers as h
import tools.forge.GUIbasics as gui
from tools.forge.interface import JSONInterface


class IndividualDisplay(gui.Section, gui.Element):
    def __init__(self, container, spell):
        self.spell = spell
        kwargs = {"name": self.spell.get('/name'), "container": container}
        gui.Section.__init__(self, **kwargs)
        gui.Element.__init__(self, **kwargs)

    def create_widgets(self):
        self.


class Popup:
    def __init__(self, master):
        self.master = master

    def create_widgets(self):
        self.name = tk.Label(win, text=self.master.__name__)
        self.school = tk.Label(win, text=self.master.school)
