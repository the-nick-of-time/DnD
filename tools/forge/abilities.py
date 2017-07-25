import tkinter as tk

from classes import Character
import helpers as h
import GUIbasics as gui
import rolling as r
import tkUtility as util

class AbilityDisplay(gui.Section):
    def __init__(self, master, character):
        gui.Section.__init__(self, master)
        self.person = character
        self.subf = tk.Frame(self.f)
        #############
        self.abilnames = ['strength', 'dexterity', 'constitution',
                          'intelligence', 'wisdom', 'charisma']
        self.abilchecks = [tk.Button(self.subf, text=a[:3].upper(), command=lambda x=a: self.roll_check(x), width=4) for (i, a) in enumerate(self.abilnames)]
        # self.scores = [util.labeledEntry(self.f, a[:3].upper(), i, 0, orient='h', width=4) for (i, a) in enumerate(self.abilnames)]
        self.scores = [tk.Entry(self.subf, width=4) for a in self.abilnames]
        self.mods = [tk.Label(self.subf, width=2) for a in self.abilnames]
        # self.abilcheck = [tk.Button(self.f, text='Check', command=) for (i, a) in enumerate(self.abilnames)]
        self.adv = tk.BooleanVar()
        self.advbutton = tk.Checkbutton(self.f, text='Advantage?', variable=self.adv)
        self.dis = tk.BooleanVar()
        self.disbutton = tk.Checkbutton(self.f, text='Disadvantage?', variable=self.dis)
        self.rolldisplay = tk.Label(self.f)
        self.draw_static()
        self.draw_dynamic()

    def draw_static(self):
        self.subf.grid(row=0, column=0)
        for (i, a) in enumerate(self.abilnames):
            self.abilchecks[i].grid(row=i, column=0)
            util.replaceEntry(self.scores[i], self.person.abilities[a])
            self.scores[i].grid(row=i, column=1)
            self.mods[i].grid(row=i, column=2)
        self.advbutton.grid(row=1, column=0)
        self.disbutton.grid(row=2, column=0)
        self.rolldisplay.grid(row=3, column=0)

    def draw_dynamic(self):
        for (i, a) in enumerate(self.abilnames):
            self.mods[i]['text'] = h.modifier(self.scores[i].get())

    def roll_check(self, abil):
        i = self.abilnames.index(abil)
        mod = h.modifier(self.scores[i].get())
        advantage = self.adv.get()
        disadvantage = self.dis.get()
        roll = '2d20h1' if (advantage and not disadvantage) else '2d20l1' if (disadvantage and not advantage) else '1d20'
        result = r.roll(roll)
        self.rolldisplay['text'] = '{}+{}={}'.format(result, mod, result+mod)

    def update_character(self):
        for (i, a) in enumerate(self.abilnames):
            self.person.abilities[a] = int(self.scores[i].get())

if __name__ == '__main__':
    win = tk.Tk()
    from interface import JSONInterface
    JSONInterface.OBJECTSPATH = '../objects/'
    jf = JSONInterface('character/Calan.character')
    app = AbilityDisplay(win, Character(jf))
    app.pack()
    win.mainloop()
