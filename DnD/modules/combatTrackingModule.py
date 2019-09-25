import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox
from typing import Callable, Optional

from . import abilityModule as abilMod
from . import dice
from .lib import abilitiesLib as abil
from .lib import combatTracking as track
from .lib import components as gui
from .lib import helpers as h
from .lib import interface as iface

Action = Callable[[], None]


class ActorDisplay(gui.Section):
    def __init__(self, container, actor: track.Actor, **kwargs):
        super().__init__(container, bd=2, relief='groove', pady=5, **kwargs)
        self.actor = actor

    def __lt__(self, other: 'ActorDisplay'):
        return self.actor < other.actor


class MonsterDisplay(ActorDisplay):
    def __init__(self, container, actor: track.Monster, **kwargs):
        super().__init__(container, actor, **kwargs)


class MonsterBuilder(tk.Toplevel):
    def __init__(self, last: Optional[track.Monster], callback: Callable[[dict], None], **kwargs):
        super().__init__(**kwargs)
        # Callback should store the data to be passed back in as `last`
        self.callback = callback
        self.last = last
        self.choice = tk.Frame(self)
        self.chooseFile = tk.Button(self.choice, text='Choose file', command=self.choose_file)
        self.chooseCustom = tk.Button(self.choice, text='Create custom', command=self.customize)
        self.focus_set()

    def choose_file(self):
        directory = iface.JsonInterface.OBJECTSPATH / 'monster'
        filename = filedialog.askopenfilename(initialdir=str(directory),
                                              filetypes=[('monster file', '*.monster')])
        self.load_file(Path(filename))

    def load_file(self, filename: Path):
        if filename.exists():
            interface = iface.JsonInterface(filename, isabsolute=True)
            spec = interface.get('/')
            average = messagebox.askyesno(message='Take average HP?')
            spec['average'] = average
            self.callback(spec)
            self.destroy()
        else:
            raise FileNotFoundError("That file does not exist. Check your spelling.")

    def customize(self):
        self.choice.destroy()
        creator = MonsterCreator(self, self.finish, self.last)
        creator.grid(0, 0)

    def finish(self, data: dict):
        self.callback(data)
        self.destroy()


class MonsterCreator(gui.Section):
    def __init__(self, container, callback: Callable[[dict], None], last: Optional[track.Monster], **kwargs):
        super().__init__(container, **kwargs)
        self.callback = callback
        self.data = {
            "name": '',
            "abilities": {name.value: 0 for name in abil.AbilityName},
            "HP": '',
            "average": True,
            "AC": '',
        }
        self.name = gui.LabeledEntry(self.f, "Enter name")
        self.name.grid(0, 0)

        self.ac = gui.LabeledEntry(self.f, 'Enter AC', width=10)
        self.ac.grid(1, 0)

        self.hp = gui.LabeledEntry(self.f, 'Enter HP as valid roll', width=10)
        self.hp.grid(2, 0)

        self.average = tk.BooleanVar()
        self.av = tk.Checkbutton(self.f, text='Take average?',
                                 variable=self.average, sticky='s')
        self.av.grid(row=3, column=1)

        self.abilities = abil.Abilities(iface.DataInterface(self.data['abilities']))
        self.abil = abilMod.AbilitiesDisplay(self.f, self.abilities,
                                             abilMod.DisplayMode.TWO_BY_THREE)
        self.abil.grid(4, 0)
        self.resolve = tk.Button(self.f, text='Finish', command=self.finish)
        if last is not None:
            self.fill_from_last(last)
        self.fill_from_data()

    def fill_from_last(self, last: track.Monster):
        self.data['name'] = last.name
        for ability in last.abilities:
            self.abilities[ability.name] = ability.score
        self.data['HP'] = last.hpRoll
        self.data['AC'] = last.AC

    def fill_from_data(self):
        self.name.replace_text(self.data['name'])
        self.ac.replace_text(self.data['AC'])
        self.hp.replace_text(self.data['HP'])
        self.average.set(self.data['average'])
        self.abil.update_view()

    def finish(self):
        self.callback(self.data)


class CharacterDisplay(ActorDisplay):
    def __init__(self, container, actor: track.Actor, **kwargs):
        super().__init__(container, actor, **kwargs)


class CharacterBuilder(tk.Toplevel):
    def __init__(self, callback: Callable[[dict], None], **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.name = gui.LabeledEntry(self, 'Character name').grid(0, 0)
        self.initiative = gui.LabeledEntry(self, 'Initiative roll').grid(1, 0)
        self.resolve = tk.Button(self, text='Finish', command=self.finish)
        self.resolve.grid(row=2, column=0)

    def finish(self):
        self.callback({
            'name': self.name.get(),
            'initiative': self.initiative.get()
        })


class MetaDisplay(gui.Section):
    def __init__(self, container, new_monster: Action, new_character: Action, close: Action, **kwargs):
        super().__init__(container, **kwargs)
        self.roller = dice.DiceRoll(self.f)
        self.roller.grid(0, 0, columnspan=3)
        self.newMonster = tk.Button(self.f, text='New Monster', command=new_monster)
        self.newMonster.grid(row=1, column=0)
        self.newCharacter = tk.Button(self.f, text='New Character', command=new_character)
        self.newCharacter.grid(row=1, column=1)
        self.QUIT = tk.Button(self.f, text='Quit', command=close)
        self.QUIT.grid(row=1, column=2)

    def __lt__(self, other):
        # sort to bottom
        return True


class Main(gui.Section):
    def __init__(self, window: tk.Tk):
        super().__init__(window)
        self.lastMonster = None
        self.meta = MetaDisplay(self.f, self.new_monster_start,
                                self.new_character_start, window.destroy)
        self.frames = h.SortedList([self.meta])
        self.draw()

    def draw(self):
        for i, f in enumerate(self.frames):
            f.grid(i % 3, i // 3)

    def new_character_start(self):
        CharacterBuilder(self.new_character_finish)

    def new_character_finish(self, data: dict):
        self.frames.append(CharacterDisplay(self.f, track.CharacterStub(data['name'], data['initiative'])))

    def new_monster_start(self):
        MonsterBuilder(self.lastMonster, self.new_monster_finish)

    def new_monster_finish(self, data):
        monster = track.Monster(data)
        self.lastMonster = monster
        self.frames.append(MonsterDisplay(self.f, monster))
        self.draw()


if __name__ == '__main__':
    win = gui.MainWindow()
    app = Main(win)
    app.pack()
    win.mainloop()
