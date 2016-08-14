import json
import collections


class JSONInterface:
    OBJECTSPATH = './tools/objects/'
    # TODO: Add functionality to merge two objects or access them in parallel

    def __init__(self, filename, PREFIX=''):
        self.shortfilename = filename.split('/')[-1].split('.')[0]
        self.filename = self.OBJECTSPATH + filename
        with open(self.filename) as f:
            data = json.load(f, object_pairs_hook=collections.OrderedDict)
            if (PREFIX):
                self.info = data[PREFIX]
            else:
                self.info = data

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
                    root[int(comp[0])] = value
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

    def write(self):
        with open(self.filename, 'w') as f:
            json.dump(obj=self.info, fp=f, indent=2)

    def __str__(self):
        return self.shortfilename

    def __repr__(self):
        return "<JSONInterface to {}>".format(self.filename)

    def get(self, path):
        if (not path.startswith('/')):
            return self._get(path, self.info)
        return self._get(path)

    def set(self, path, value):
        if (not path.startswith('/')):
            return self._set(path, value, self.info)
        return self._set(path, value)

    def __add__(self, other):
        return LinkedInterface(self, other)


class LinkedInterface(JSONInterface):
    def __init__(self, *ifaces):
        self.searchpath = collections.OrderedDict(
            (str(iface), iface) for iface in ifaces)

    def __add__(self, other):
        if (isinstance(other, LinkedInterface)):
            self.searchpath.update(other.searchpath)

    def get(self, path):
        s = path.split('/')
        filename = s[0] if s[0] else s[1]
        if (filename in self.searchpath):
            return self.searchpath[filename]._get(path[len(filename):])
        else:
            for name, iface in self.searchpath.items():
                rv = iface._get(path)
                if (rv is not None):
                    return rv

    def set(self, path, value):
        s = path.split('/')
        filename = s[0] if s[0] else s[1]
        if (filename in self.searchpath):
            return self.searchpath[filename]._set(path[len(filename):])
        else:
            for name, iface in self.searchpath.items():
                rv = iface._set(path, value)
                if (rv):
                    return rv
