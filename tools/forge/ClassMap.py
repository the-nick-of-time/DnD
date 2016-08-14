import re

import tools.forge._classes as c
import tools.forge.helpers as h
import tools.forge.interface as iface


class ClassMap:
    def __init__(self, s):
        # Takes in a string of the form Class [(Subclass)] Level,...
        # TODO: _classes should be a list of Class objects
        self._classes = []
        self._subclasses = []
        self.levels = []
        self.classes = []  # Class objects

        L = s.split(',')
        for substr in L:
            desc = filter(None, re.split(r'[\s()]', substr))
            if (len(desc) == 2):
                self._classes.append(desc[0])
                self._subclasses.append('')
                self.levels.append(int(desc[1]))
            else:
                self._classes.append(desc[0])
                self._subclasses.append(desc[1])
                self.levels.append(int(desc[2]))

    def __len__(self):
        return len(self._classes)

    def __str__(self):
        out = []
        for (C, S, L) in zip(self._classes, self._subclasses, self.levels):
            out.extend((C, (''.join((' (', S, ') ')) if S else ' '), str(L),
                        ', '))
        return ''.join(out[:-1])

    def sum(self):
        return sum(self.levels)

    def hook(self):
        loc = '/class/{}.class'
        alt = '/class/{}.{}.sub.class'
        for (C, S, L) in zip(self._classes, self._subclasses, self.levels):
            if (not S):
                file_ = loc.format(C)
                subfile_ = ''
            else:
                subfile_ = alt.format(C, S)
            jf = iface.JSONInterface(file_)
