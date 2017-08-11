import re
import json
import os

import classes as c

d = os.path.dirname(os.path.abspath(__file__))
with open(d + '/conditions.json') as f:
    condition_defs = json.load(f)

D20 = '1d20'
D20_LUCK = '1d20r1'
ADV = '2d20h1'
ADV_LUCK = '2d20r1h1'
DIS = '2d20l1'
DIS_LUCK = '2d20r1l1'


def modifier(score):
    return (int(score) - 10) // 2


def d20_roll(adv=False, dis=False, luck=False):
    if (adv and not dis):
        if (luck):
            return ADV_LUCK
        else:
            return ADV
    elif (dis and not adv):
        if (luck):
            return DIS_LUCK
        else:
            return DIS
    else:
        if (luck):
            return D20_LUCK
        else:
            return D20



def shorten(effect):
    """Takes an effects string and returns the first sentence."""
    if (effect):
        match = re.match('^.*?[\.\n]', effect)
        if (match is not None):
            return match.group()
        return ""
    else:
        return ""


def clean(name):
    return name.replace(' ', '_').replace('\'', '@').replace('/', '&')


def unclean(name):
    return name.replace('_', ' ').replace('@', '\'').replace('&', '/')


def pull_from(*args):
    """args is a tuple of tkinter widgets with .get() methods."""
    data = tuple(widget.get() for widget in args)
    def decorator(func):
        def decorated():
            return func(*data)
        decorated.__name__ = func.__name__
        return decorated
    return decorator


def type_select(extension):
    """Find the class corresponding to a file's extension."""
    tree = {
        "apparel": {"magic": {"": c.MagicArmor},
                    "": c.Armor},
        "character": {"": c.Character},
        "class": {"": c.Class},
        "item": {"magic": {"": c.MagicItem},
                 "": c.Item},
        "spell": {"": c.Spell},
        "treasure": {"": c.Item},
        "weapon": {
            "magic": {"ranged": {"": c.MagicRangedWeapon},
                      "": c.MagicWeapon},
            "ranged": {"magic": {"": c.MagicRangedWeapon},
                       "": c.RangedWeapon},
            "": c.Weapon
        }
    }
    steps = extension.split('.')
    steps[0] = ''  # We don't care about the initial name, even if given
    location = tree
    for step in reversed(steps):
        location = location[step]
    return location


def find_file(name, type_):
    from interface import JSONInterface
    directory = '{direc}/{name}'
    location = type_.split(sep='.')
    if (location[0] == ''):
        # Leading . indicates name of object is included in path
        location[0] = clean(name)
        deeper = False
    else:
        deeper = True
    filename = directory.format(
        direc=location[-1], name='.'.join(location))
    try:
        iface = JSONInterface(filename)
        return iface
    except FileNotFoundError:
        raise


def path_follower(path, alltheway=False):
    from interface import JSONInterface
    match = re.match('/*(\w*.*\.[a-z]*)(/.*)', path)
    try:
        tofile = match.group(1)
        infile = match.group(2)
    except IndexError:
        raise ValueError('Needs to be given as a path to a file then within'
                         'the file to the desired data')
    if (os.path.isfile(JSONInterface.OBJECTSPATH + tofile)):
        jf = JSONInterface(tofile)
        if (alltheway):
            # The data within the sought file
            return jf.get(infile)
        else:
            # The file and path within the file separately, to work with
            #   classes.Resource
            return (jf, infile)
    else:
        raise FileNotFoundError
