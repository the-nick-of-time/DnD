import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from tkinter import messagebox
from typing import Callable, Optional

import abilityModule as abilMod
import dice
import lib.abilitiesLib as abil
import lib.combatTracking as track
import lib.components as gui
import lib.helpers as h
import lib.interface as iface

Action = Callable[[], None]
Deleter = Callable[['ActorDisplay'], None]


class ActorDisplay(gui.Section):
    def __init__(self, container, actor: track.Actor, deleter: Deleter, **kwargs):
        super().__init__(container, bd=2, relief='groove', pady=5, **kwargs)
        self.actor = actor
        image = Path(__file__).parent / 'assets' / 'close.png'
        self.deleteMark = tk.PhotoImage(file=str(image))
        self.delete = tk.Button(self.f, command=lambda: deleter(self),
                                image=self.deleteMark)
        self.name = tk.Label(self.f, text=self.actor.name)
        self.initiative = tk.Label(self.f, text=f'Initiative: {self.actor.initiative}')
        self.draw()

    def draw(self):
        self.name.grid(row=0, column=0)
        self.initiative.grid(row=1, column=0)
        self.delete.grid(row=0, column=999, sticky='ne')

    def __lt__(self, other: 'ActorDisplay'):
        if isinstance(other, MetaDisplay):
            return True
        return self.actor < other.actor


class MonsterDisplay(ActorDisplay):
    def __init__(self, container, actor: track.Monster, deleter: Deleter, **kwargs):
        super().__init__(container, actor, deleter, **kwargs)


class MonsterBuilder(tk.Toplevel):
    def __init__(self, last: Optional[track.Monster], callback: Callable[[dict], None], **kwargs):
        super().__init__(**kwargs)
        # Callback should store the data to be passed back in as `last`
        self.callback = callback
        self.last = last
        self.choice = tk.Frame(self)
        self.choice.grid(row=0, column=0)
        self.chooseFile = tk.Button(self.choice, text='Choose file', command=self.choose_file)
        self.chooseFile.grid(row=0, column=0)
        self.chooseCustom = tk.Button(self.choice, text='Create custom', command=self.customize)
        self.chooseCustom.grid(row=0, column=1)
        self.focus_set()

    def choose_file(self):
        directory = iface.JsonInterface.OBJECTSPATH / 'monster'
        filename = filedialog.askopenfilename(initialdir=str(directory),
                                              filetypes=[('monster file', '*.monster')])
        if filename:
            self.load_file(Path(filename))
        else:
            self.destroy()

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


# TODO: customize from gui.Query
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
                                 variable=self.average)
        self.av.grid(row=2, column=1, sticky='s')

        self.abilities = abil.Abilities(iface.DataInterface(self.data['abilities']))
        self.abil = abilMod.AbilitiesDisplay(self.f, self.abilities,
                                             abilMod.DisplayMode.TWO_BY_THREE)
        self.abil.grid(3, 0)
        self.resolve = tk.Button(self.f, text='Finish', command=self.finish)
        self.resolve.grid(row=4, column=0, columnspan=2)

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

    def finish(self):
        self.callback(self.data)


class CharacterDisplay(ActorDisplay):
    def __init__(self, container, actor: track.Actor, deleter: Deleter, **kwargs):
        super().__init__(container, actor, deleter, **kwargs)


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
        gui.Query(self.new_character_finish, "Character name", "Initiative roll")

    def new_character_finish(self, data: dict):
        character = track.CharacterStub(data['Character name'], data['Initiative roll'])
        display = CharacterDisplay(self.f, character, self.delete)
        self.frames.append(display)
        self.draw()

    def new_monster_start(self):
        MonsterBuilder(self.lastMonster, self.new_monster_finish)

    def new_monster_finish(self, data):
        monster = track.Monster(data)
        self.lastMonster = monster
        self.frames.append(MonsterDisplay(self.f, monster, self.delete))
        self.draw()

    def delete(self, frame: ActorDisplay):
        frame.destroy()
        self.frames.remove(frame)
        self.draw()


if __name__ == '__main__':
    win = gui.MainWindow()
    app = Main(win)
    app.pack()
    win.mainloop()
