import collections
import json

import jsonpointer


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
        if path == '/':
            return self.info
        return jsonpointer.resolve_pointer(self.info, path, None)

    def delete(self, path):
        if self.readonly:
            raise ReadonlyError('{} is a readonly file'.format(self.filename))
        if path == '/':
            self.info = {}
        obj = jsonpointer.resolve_pointer(self.info, path, None)
        if obj is not None:
            del obj

    def set(self, path, value):
        if self.readonly:
            raise ReadonlyError('{} is a readonly file'.format(self.filename))
        if path == '/':
            self.info = value
        jsonpointer.set_pointer(self.info, path, value)

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
    def __init__(self, filename, path: str, readonly=False, isabsolute=False):
        super().__init__(filename, readonly=readonly, isabsolute=isabsolute)
        self.path = path.rstrip('/')

    def _total_path(self, path):
        return self.path + '/' + path

    def get(self, path):
        return super().get(self._total_path(path))

    def set(self, path, value):
        super().set(self._total_path(path), value)

    def delete(self, path):
        super().delete(self._total_path(path))


class ReadonlyError(Exception):
    pass
