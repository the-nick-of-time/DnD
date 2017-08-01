import json
import collections
import re
from os.path import abspath


class JSONInterface:
    OBJECTSPATH = './tools/objects/'
    # OBJECTSPATH = abspath('.') + '/tools/objects/'
    # TODO: Add functionality to merge two objects or access them in parallel

    def __init__(self, filename):
        broken = filename.split('/')[-1].split('.')
        self.shortfilename = ' '.join(reversed(broken[:len(broken) // 2]))
        # TODO: Unclean filename?
        self.filename = self.OBJECTSPATH + filename
        with open(self.filename) as f:
            data = json.load(f, object_pairs_hook=collections.OrderedDict)
            self.info = data

    def __str__(self):
        return self.shortfilename

    def __repr__(self):
        return "<JSONInterface to {}>".format(self.filename)

    def __add__(self, other):
        if (isinstance(other, (JSONInterface, LinkedInterface))):
            return LinkedInterface(self, other)
        else:
            raise TypeError('You can only add a JSONInterface or a '
                            'LinkedInterface to a JSONInterface')

    def get(self, path):
        if (path == '/'):
            return self.info
        if (not path.startswith('/')):
            return self._get(path, self.info)
        return self._get(path)

    def delete(self, path):
        if (path == '/'):
            del self.info
            return True
        if (not path.startswith('/')):
            return self._delete(path, self.info)
        return self._delete(path)

    def set(self, path, value):
        if (path == '/'):
            return False
        if (not path.startswith('/')):
            return self._set(path, value, self.info)
        return self._set(path, value)

    def write(self):
        with open(self.filename, 'w') as f:
            json.dump(obj=self.info, fp=f, indent=2)

    def _get(self, path, root=None):
        try:
            if (root is None):
                return self._get(path, self.info)
            comp = path.split(sep='/', maxsplit=1)
            if (len(comp) == 1):
                # Terminal
                if (isinstance(root, list)):
                    return root[int(comp[0])]
                else:
                    return root[comp[0]]
            if (comp[0] == ''):
                # Intitial
                return self._get(comp[1], self.info)
            # Recurse
            if(isinstance(root, list)):
                return self._get(comp[1], root[int(comp[0])])
            else:
                return self._get(comp[1], root[comp[0]])
        except (KeyError, IndexError):
            return None

    def _set(self, path, value, root=None):
        try:
            if (root is None):
                return self._set(path, value, self.info)
            comp = path.split(sep='/', maxsplit=1)
            if (len(comp) == 1):
                # Terminal
                if (isinstance(root, list)):
                    i = int(comp[0])
                    if (i >= len(root)):
                        # Writing beyond end of list, pad with None
                        root = root + [None for each in range(len(root), i)] + [value]
                    else:
                        # Valid
                        root[i] = value
                else:
                    root[comp[0]] = value
                return True
            if (comp[0] == ''):
                # Intitial
                return self._set(comp[1], value, self.info)
            # Recurse
            if(isinstance(root, list)):
                return self._set(comp[1], value, root[int(comp[0])])
            else:
                return self._set(comp[1], value, root[comp[0]])
        except (KeyError, IndexError):
            return False

    def _delete(self, path, root=None):
        try:
            if (root is None):
                return self.delete(path, self.info)
            comp = path.split(sep='/', maxsplit=1)
            if (len(comp) == 1):
                # Terminal
                if (isinstance(root, list)):
                    del root[int(comp[0])]
                else:
                    del root[comp[0]]
                return True
            if (comp[0] == ''):
                # Intitial
                return self._delete(comp[1], self.info)
            # Recurse
            if(isinstance(root, list)):
                return self._delete(comp[1], root[int(comp[0])])
            else:
                return self._delete(comp[1], root[comp[0]])
        except (KeyError, IndexError):
            return False



class LinkedInterface:
    def __init__(self, *ifaces):
        self.searchpath = collections.OrderedDict(
            ((str(iface), iface) for iface in ifaces))

    def __add__(self, other):
        if (isinstance(other, LinkedInterface)):
            self.searchpath.update(other.searchpath)
            return self
        elif (isinstance(other, JSONInterface)):
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
        if (filename in self.searchpath):
            # find the result in the specified file
            return self.searchpath[filename]._get(remaining)
        elif (filename == '*'):
            # Find all results in all files
            # Search in more general files then override with more specific
            first = True
            for name, iface in self.searchpath.items():
                found = iface.get(remaining)
                if (found is not None):
                    if (first):
                        rv = found
                        first = False
                        if (isinstance(rv, list)):
                            add = list.extend
                        elif (isinstance(rv, dict)):
                            add = dict.update
                    else:
                        add(rv, found)
            return rv
        else:
            # Find one result in the most specific file you can find it in
            for name, iface in reversed(self.searchpath.items()):
                rv = iface.get(path)
                if (rv is not None):
                    return rv
            return None

    def set(self, path, value):
        s = path.split('/')
        filename, remaining = (s[0], s[1:]) if s[0] else (s[1], s[2:])
        remaining = '/'.join(remaining)
        if (filename in self.searchpath):
            return self.searchpath[filename]._set(remaining, value)
        else:
            for name, iface in reversed(self.searchpath.items()):
                rv = iface._set(path, value)
                if (rv):
                    return rv
            return False
