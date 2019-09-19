import collections
import json
from pathlib import Path
from typing import Dict, Any, Union

import jsonpointer

from . import helpers as h


class DataInterface:
    class JsonPointerCache:
        def __init__(self):
            self.cache = {}

        def __getitem__(self, key: str) -> jsonpointer.JsonPointer:
            if key not in self.cache:
                self.cache[key] = jsonpointer.JsonPointer(key)
            return self.cache[key]

    def __init__(self, data: Union[list, Dict[str, Any]], readonly=False, basepath=""):
        self.data = data
        self.basepath = basepath.rstrip('/')
        self.readonly = readonly
        self._cache = type(self).JsonPointerCache()

    def __iter__(self):
        yield from self.data.items()

    def get(self, path: str):
        if self.basepath + path == '/':
            return self.data
        if path == '/':
            path = ''
        pointer = self._cache[self.basepath + path]
        return pointer.resolve(self.data, None)

    def delete(self, path):
        if self.readonly:
            raise ReadonlyError('{} is readonly'.format(self.data))
        if self.basepath + path == '/':
            self.data = {}
            return
        if path == '/':
            path = ''
        pointer = self._cache[self.basepath + path]
        subdoc, key = pointer.to_last(self.data)
        del subdoc[key]

    def set(self, path, value):
        if self.readonly:
            raise ReadonlyError('{} is readonly'.format(self.data))
        if self.basepath + path == '/':
            self.data = value
            return
        if path == '/':
            path = ''
        pointer = self._cache[self.basepath + path]
        pointer.set(self.data, value)

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
            return LinkedInterface(self, other)
        elif isinstance(other, LinkedInterface):
            return other.__add__(self)
        else:
            raise TypeError("You can only add a JsonInterface or a "
                            "MultiInterface to a JsonInterface")

    def __repr__(self):
        return "<JsonInterface to {}>".format(self.filename)

    def __str__(self):
        return self.shortFilename

    def write(self):
        if self.readonly:
            return
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)


class LinkedInterface:
    def __init__(self, *interfaces: JsonInterface):
        """interfaces should come in order from least to most specific"""
        self.searchpath = collections.OrderedDict(
            (inter.filename, inter) for inter in interfaces)

    def __add__(self, other):
        if isinstance(other, LinkedInterface):
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


class ReadonlyError(Exception):
    pass


class PathError(ValueError):
    pass
