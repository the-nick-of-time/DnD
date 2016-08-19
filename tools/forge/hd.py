import math

from tools.forge.ClassMap import ClassMap
import tools.forge.interface as iface
import tools.libraries.rolling as r


class SingleHandler:
    def __init__(self, character, whichclass, level):
        # Both should be JSONInterfaces
        self.character = character
        self.whichclass = whichclass
        self.hdtype = self.whichclass.get('/hit_dice')
        self.hdpath = '/HP/HD/{}'.format(self.hdtype)
        self.level = level

    def spend(self):
        remaining = self.character.get(self.hdpath)
        if (remaining > 0):
            self.character.set(self.hdpath, remaining - 1)
            return r.roll(self.hdtype)
        else:
            return 0

    def regain(self):
        remaining = self.character.get(self.hdpath)
        if (remaining >= self.level):
            self.character.set(self.hdpath, self.level)
        else:
            self.character.set(self.hdpath, remaining + 1)

    def reset(self):
        self.character.set(self.hdpath, self.level)

    def rest(self):
        remaining = self.character.get(self.hdpath)
        self.character.set(self.hdpath, remaining + math.ceil(self.level / 2))
        if (self.character.get(self.hdpath) > self.level):
            self.reset()


class MultiHandler:
    def __init__(self, character):
        self.character = character
        self.classes = ClassMap(self.character.get('/level'))
        self.hd = {}
        self.make()

    def make(self):
        for c, lv in self.classes:
            self.hd.update({str(c): SingleHandler(self.character, c, lv)})

    def reset(self):
        for obj in self.hd:
            obj.reset()

    def rest(self):
        for obj in self.hd:
            obj.rest()

    def spend(self, which):
        self.hd[which].spend()

    def regain(self, which):
        self.hd[which].regain()
