import json
import collections


class JSONInterface:
    OBJECTSPATH = './tools/objects/'

    def __init__(self, filename, PREFIX=''):
        self.filename = self.OBJECTSPATH + filename
        with open(self.filename) as f:
            data = json.load(f, object_pairs_hook=collections.OrderedDict)
            if (PREFIX):
                self.info = data[PREFIX]
            else:
                self.info = data

    def get(self, path, root=None):
        try:
            if (root is None):
                return self.get(path, self.info)
            comp = path.split(sep='/', maxsplit=1)
            if (len(comp) == 1):
                # Terminal
                return root[_conv(comp[0])]
            if (comp[0] == ''):
                # Intitial
                return self.get(comp[1], self.info)
            # Recurse
            if(isinstance(root, list)):
                return self.get(comp[1], root[int(comp[0])])
            else:
                return self.get(comp[1], root[comp[0]])
        except (KeyError, IndexError):
            return ""

    def set(self, path, value, root=None):
        try:
            if (root is None):
                return self.set(path, value, self.info)
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
                return self.set(comp[1], value, self.info)
            # Recurse
            if(isinstance(root, list)):
                return self.set(comp[1], value, root[int(comp[0])])
            else:
                return self.set(comp[1], value, root[comp[0]])
        except (KeyError, IndexError):
            return False

    def write(self):
        with open(self.filename, 'w') as f:
            json.dump(obj=self.info, fp=f, indent=2)


def _conv(val):
    try:
        return int(val)
    except ValueError:
        return val
