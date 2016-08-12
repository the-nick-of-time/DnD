import re

class ClassMap:
    def __init__(self, s):
        # Takes in a string of the form Class [(Subclass)] Level,...
        # TODO: classes should be a list of Class objects
        self.classes = []
        self.subclasses = []
        self.levels = []

        L = s.split(',')
        for substr in L:
            desc = filter(None, re.split(r'[\s()]' ,substr))
            if (len(desc) == 2):
                self.classes.append(desc[0])
                self.subclasses.append('')
                self.levels.append(int(desc[1]))
            else:
                self.classes.append(desc[0])
                self.subclasses.append(desc[1])
                self.levels.append(int(desc[2]))

    def __len__(self):
        return len(self.classes)

    def __str__(self):
        out = []
        for (C, S, L) in zip(self.classes, self.subclasses, self.levels):
            out.extend((C, (''.join((' (', S, ') ')) if S else ' '), str(L), ', '))
        return ''.join(out[:-1])

    def sum(self):
        return sum(self.levels)

    def hook(self):
        direc = '/'
        for (C, S, L) in zip(self.classes, self.subclasses, self.levels):
