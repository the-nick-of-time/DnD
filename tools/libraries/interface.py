import collections
import json
from pathlib import Path
from typing import Dict, Any, Union

import dpath

import helpers as h


class DataInterface:
    def __init__(self, data: Union[list, Dict[str, Any]], readonly=False, basepath=""):
        self.data = data
        self.basepath = basepath.rstrip('/')
        self.readonly = readonly

    def __iter__(self):
        yield from self.data.items()

    def get(self, path: str):
        return dpath.get(self.data, self.basepath + path)

    def delete(self, path):
        if self.readonly:
            raise ReadonlyError('{} is readonly'.format(self.data))
        dpath.delete(self.data, self.basepath + path)

    def set(self, path, value):
        if self.readonly:
            raise ReadonlyError('{} is readonly'.format(self.data))
        dpath.set(self.data, self.basepath + path, value)

    def cd(self, path, readonly=False):
        return DataInterface(self.data, readonly=self.readonly or readonly, basepath=path)


class JsonInterface(DataInterface):
    OBJECTSPATH = Path('./tools/objects/')
    EXTANT = {}

    def __new__(cls, filename, **kwargs):
        if kwargs.get('isabsolute', False):
            totalpath = filename
        else:
            totalpath = cls.OBJECTSPATH / filename
        if totalpath in cls.EXTANT:
            return cls.EXTANT[totalpath]
        else:
            obj = super().__new__(cls)
            return obj

    def __init__(self, filename, readonly=False, isabsolute=False):
        self.shortFilename = h.unclean(filename)
        if isabsolute:
            self.filename = filename
        else:
            self.filename = self.OBJECTSPATH / filename
        with open(self.filename, 'r') as f:
            data = json.load(f, object_pairs_hook=collections.OrderedDict)
            super().__init__(data, readonly)
        self.EXTANT[self.filename] = self

    def __add__(self, other):
        if isinstance(other, JsonInterface):
            return MultiInterface(self, other)
        elif isinstance(other, MultiInterface):
            return other.__add__(self)
        else:
            raise TypeError("You can only add a JsonInterface or a "
                            "MultiInterface to a JsonInterface")

    def __repr__(self):
        return "<JSONInterface to {}>".format(self.filename)

    def __str__(self):
        return self.shortFilename

    def write(self):
        if self.readonly:
            return
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)


class MultiInterface:
    def __init__(self, *interfaces: JsonInterface):
        """interfaces should come in order from least to most specific"""
        self.searchpath = collections.OrderedDict(
            (inter.filename, inter) for inter in interfaces)

    def __add__(self, other):
        if isinstance(other, MultiInterface):
            self.searchpath.update(other.searchpath)
            return self
        elif isinstance(other, JsonInterface):
            self.searchpath[other.filename] = other
            return self
        else:
            raise TypeError("You can only add a JsonInterface or a "
                            "MultiInterface to a MultiInterface")

    def _most_to_least(self):
        return reversed(self.searchpath.values())

    def _least_to_most(self):
        return self.searchpath.values()

    def get(self, path: str):
        split = path.split(':')
        if len(split) == 1:
            filename = None
            path = split[0]
        elif len(split) == 2:
            filename = split[0]
            path = split[1]
        else:
            raise PathError("Format should be filename:/path")
        if filename in self.searchpath:
            return self.searchpath[filename].get(path)
        elif filename == '*':
            # Find all results in all files
            # Search in more general files then override with more specific
            rv = None
            for name, iface in self._least_to_most():
                found = iface.get("/" + path)
                if found is not None:
                    if rv is None:
                        if isinstance(rv, list):
                            add = list.extend
                            rv = found
                        elif isinstance(rv, dict):
                            add = dict.update
                            rv = found
                        else:
                            # Aggregate individual values into a list
                            rv = [found]
                            add = list.append
                    else:
                        add(rv, found)
            return rv
        else:
            # Find one result in the most specific file you can find it in
            for name, iface in self._most_to_least():
                rv = iface.get(path)
                if rv is not None:
                    return rv
            return None


class JSONInterface:
    OBJECTSPATH = './tools/objects/'
    EXTANT = {}

    def __new__(cls, filename, **kwargs):
        # If there is already an interface to the file open, return that
        #   instead of opening a new one
        if JSONInterface.OBJECTSPATH + filename in JSONInterface.EXTANT:
            return JSONInterface.EXTANT[JSONInterface.OBJECTSPATH + filename]
        else:
            obj = super().__new__(cls)
            return obj

    def __init__(self, filename, readonly=False, isabsolute=False):
        self.readonly = readonly
        self.shortfilename = filename.split('/')[-1]
        if isabsolute:
            self.filename = filename
        else:
            self.filename = self.OBJECTSPATH + filename
        with open(self.filename) as f:
            data = json.load(f, object_pairs_hook=collections.OrderedDict)
            self.info = data
        JSONInterface.EXTANT.update({self.filename: self})

    def __str__(self):
        return self.shortfilename

    def __repr__(self):
        return "<JSONInterface to {}>".format(self.filename)

    def __add__(self, other):
        if isinstance(other, JSONInterface):
            return LinkedInterface(self, other)
        if isinstance(other, LinkedInterface):
            # Use LinkedInterface's add method
            return other + self
        else:
            raise TypeError('You can only add a JSONInterface or a '
                            'LinkedInterface to a JSONInterface')

    def __iter__(self):
        yield self

    def get(self, path: str):
        return dpath.get(self.info, path)

    def delete(self, path):
        if self.readonly:
            raise ReadonlyError('{} is a readonly file'.format(self.filename))
        dpath.delete(self.info, path)

    def set(self, path, value):
        if self.readonly:
            raise ReadonlyError('{} is a readonly file'.format(self.filename))
        dpath.set(self.info, path, value)

    def cd(self, path):
        # TODO: should subinterfaces be forced readonly? or configurable?
        return SubInterface(self, path, readonly=self.readonly,
                            isabsolute=self.filename.startswith(self.OBJECTSPATH))

    def write(self):
        if self.readonly:
            return
        with open(self.filename, 'w') as f:
            json.dump(obj=self.info, fp=f, indent=2)


class LinkedInterface:
    def __init__(self, *ifaces):
        self.searchpath = collections.OrderedDict(
            ((str(iface), iface) for iface in ifaces))

    def __add__(self, other):
        if isinstance(other, LinkedInterface):
            self.searchpath.update(other.searchpath)
            return self
        elif isinstance(other, JSONInterface):
            self.searchpath.update({str(other): other})
            return self
        else:
            raise TypeError('You can only add a JSONInterface or a '
                            'LinkedInterface to a LinkedInterface')

    def __str__(self):
        return ', '.join(reversed(self.searchpath.keys()))

    def __repr__(self):
        return '<LinkedInterface to {}>'.format(str(self))

    def __iter__(self):
        return (iface for iface in self.searchpath.values())

    def get(self, path):
        s = path.split('/')
        filename, remaining = (s[0], s[1:]) if s[0] else (s[1], s[2:])
        remaining = '/'.join(remaining)
        if filename in self.searchpath:
            # find the result in the specified file
            return self.searchpath[filename].get(remaining)
        elif filename == '*':
            # Find all results in all files
            # Search in more general files then override with more specific
            rv = None
            for name, iface in self.searchpath.items():
                found = iface.get("/" + remaining)
                if found is not None:
                    if rv is None:
                        if isinstance(rv, list):
                            add = list.extend
                            rv = found
                        elif isinstance(rv, dict):
                            add = dict.update
                            rv = found
                        else:
                            # Aggregate individual values into a list
                            rv = [found]
                            add = list.append
                    else:
                        add(rv, found)
            return rv
        else:
            # Find one result in the most specific file you can find it in
            for name, iface in reversed(self.searchpath.items()):
                rv = iface.get(path)
                if rv is not None:
                    return rv
            return None

    def set(self, path, value):
        s = path.split('/')
        filename, remaining = (s[0], s[1:]) if s[0] else (s[1], s[2:])
        remaining = '/'.join(remaining)
        if filename in self.searchpath:
            return self.searchpath[filename].set(remaining, value)
        else:
            for name, iface in reversed(self.searchpath.items()):
                rv = iface.set(path, value)
                if rv:
                    return rv
            return False


class SubInterface(JSONInterface):
    def __init__(self, parent: JSONInterface, path: str, readonly=False, isabsolute=False):
        # Calling it with parent.filename feels a little hacky but worth it to get the inheritance
        # and it works because two `JSONInterface`s with the same filename will be the same object
        super().__init__(parent.filename, readonly=readonly, isabsolute=isabsolute)
        self.path = path.rstrip('/')

    def _total_path(self, path):
        return self.path + path

    def get(self, path):
        return super().get(self._total_path(path))

    def set(self, path, value):
        super().set(self._total_path(path), value)

    def delete(self, path):
        super().delete(self._total_path(path))

    def cd(self, path) -> 'SubInterface':
        return SubInterface(self, self.path + path, readonly=self.readonly,
                            isabsolute=self.filename.startswith(self.OBJECTSPATH))


class ReadonlyError(Exception):
    pass


class PathError(ValueError):
    pass
