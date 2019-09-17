import collections
import re

import classes as c
import helpers as h
import interface as iface


class ClassMap:
    """Represents the total list of class levels that a character has.

    Data:
    classes: a dictionary mapping class names to Class objects.

    Methods:
    sum: Returns the total level of the character.
    names: Returns a list of class names that that the character has.
    level_up: Given a main class name and an optional subclass name, add a
        level in that class. If a subclass is given, add that subclass to the
        main class. Returns a tuple of the Class object and the final level.
    apply_subclass: Given the main class name and subclass name, add a subclass
        to the main class named.
    """
    def __init__(self, s):
        # Takes in a string of the form Class [(Subclass)] Level,...
        self._classes = []
        self._subclasses = []
        self.levels = []
        self.classes = collections.OrderedDict()

        split = s.split(',')
        for substr in split:
            pattern = r'\s*([a-zA-Z\']+)\s*(\(([a-zA-Z\'\s]+)\))?\s*([0-9]+)'
            desc_ = re.match(pattern, substr).groups()
            desc = [str(item) for item in desc_ if item is not None]
            if len(desc) == 2:
                self._classes.append(desc[0])
                self._subclasses.append('')
                self.levels.append(int(desc[1]))
            else:
                self._classes.append(desc[0])
                self._subclasses.append(desc[2])
                self.levels.append(int(desc[3]))

        self.hook()

    def __len__(self):
        return len(self._classes)

    def __str__(self):
        out = []
        for (C, S, L) in zip(self._classes, self._subclasses, self.levels):
            out.extend((C, (''.join((' (', S, ') ')) if S else ' '), str(L),
                        ', '))
        return ''.join(out[:-1])

    def __iter__(self):
        return (tup for tup in zip(self.classes.keys(), self.classes.values(),
                                   self.levels))

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.classes[key]
        elif isinstance(key, int):
            for i, v in enumerate(self.classes.values()):
                if i == key:
                    return v
            raise IndexError
        raise TypeError

    def sum(self):
        return sum(self.levels)

    def names(self):
        return self._classes

    def hook(self):
        main = 'class/{}.class'
        sub = 'class/{}.{}.sub.class'
        super_ = 'class/{}.super.class'
        for (class_, subclass, L) in zip(self._classes, self._subclasses, self.levels):
            class_ = h.clean(class_)
            subclass = h.clean(subclass)
            file_ = main.format(class_)
            subfile_ = sub.format(class_, subclass)
            mainclass = iface.JsonInterface(file_)
            try:
                subclass = iface.JsonInterface(subfile_)
                subclassfound = True
            except FileNotFoundError:
                subclassfound = False
            superclasses = [iface.JsonInterface(super_.format(name))
                            for name in mainclass.get('/superclass')]
            # noinspection PyUnboundLocalVariable
            if subclassfound and subclass.get('/superclass'):
                superclasses.extend([iface.JsonInterface(super_.format(name))
                                     for name in subclass.get('/superclass')])
            if subclassfound:
                jf = iface.LinkedInterface(*superclasses, mainclass,
                                           subclass)
                # self.classes.update(
                #     {str(mainclass): iface.LinkedInterface(*superclasses,
                #                                            mainclass,
                #                                            subclass)})
            else:
                jf = iface.LinkedInterface(*superclasses, mainclass)
                # self.classes.update(
                #     {str(mainclass): iface.LinkedInterface(*superclasses,
                #                                            mainclass)})
            self.classes.update({class_: c.Class(jf, L)})

    def level_up(self, name, subclassname=''):
        if name in self._classes:
            i = self._classes.index(name)
            self.levels[i] += 1
            lev = self.levels[i]
            self.classes[name].level += 1
        else:
            self._classes.append(name)
            self.levels.append(1)
            lev = 1
            self._subclasses.append(subclassname)
            self.hook()
        return self.classes[name], lev

    def apply_subclass(self, mainclass, subclass):
        i = self._classes.index(mainclass)
        self._subclasses[i] = subclass
        self.hook()


class RaceMap:
    """Represents a race and possibly subrace.

    Data:
    core: A Race object.

    Methods:
    get_feature_links: Returns a dict of race features as they show up in a
        character file.
    """
    def __init__(self, s):
        pattern = '\s*([\w-]+)\s*\(?([\w-]+)?\)?\s*'
        res = re.match(pattern, s).groups()
        self.race = res[0]
        self.subrace = res[1] or ''
        self.hook()

    def __getattr__(self, key):
        return self.core.__getattribute__(key)

    def __str__(self):
        return self.race + (' ({})'.format(self.subrace)
                            if self.subrace else '')

    def hook(self):
        main = 'race/{}.race'.format(self.race)
        sub = 'race/{}.{}.sub.race'.format(self.race, self.subrace)
        mainjf = iface.JsonInterface(main)
        if self.subrace:
            subjf = iface.JsonInterface(sub)
            self.core = c.Race(iface.LinkedInterface(mainjf, subjf), str(self))
        else:
            # For the sake of having a consistent API it needs to be a LinkedInterface
            # noinspection PyAttributeOutsideInit
            self.core = c.Race(iface.LinkedInterface(mainjf), str(self))

    def get_feature_links(self):
        rv = collections.OrderedDict()
        main = 'race/{}.race'.format(self.race)
        sub = 'race/{}.{}.sub.race'.format(self.race, self.subrace)
        mainjf = iface.JsonInterface(main)
        for name in (mainjf.get('/features') or []):
            rv[name] = main + '/features/' + name
        if self.subrace:
            subjf = iface.JsonInterface(sub)
            for name in (subjf.get('/features') or []):
                rv[name] = sub + '/features/' + name
        return rv
