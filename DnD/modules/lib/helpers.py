import functools
import json
import os
import re

import dndice as r

D20 = r.compile('1d20')
D20_LUCK = r.compile('1d20r1')
ADV = r.compile('2d20h1')
ADV_LUCK = r.compile('2d20r1h1')
DIS = r.compile('2d20l1')
DIS_LUCK = r.compile('2d20r1l1')


def modifier(score):
    return (int(score) - 10) // 2


def d20_roll(adv=False, dis=False, luck=False):
    if adv and not dis:
        if luck:
            return ADV_LUCK
        else:
            return ADV
    elif dis and not adv:
        if luck:
            return DIS_LUCK
        else:
            return DIS
    else:
        if luck:
            return D20_LUCK
        else:
            return D20


def shorten(effect):
    """Takes an effects string and returns the first sentence."""
    if effect:
        match = re.match(r'^.*?[.\n]', effect)
        if match is not None:
            return match.group()
        return ""
    else:
        return ""


def sanitize_filename(name: str) -> str:
    """Translates problematic characters in a filename into happier ones."""
    return name.translate(str.maketrans(" '/:", "_@&$"))


def readable_filename(name: str) -> str:
    """Translates back into the actual, problematic characters."""
    return name.translate(str.maketrans("_@&$", " '/:"))


def pull_from(*args):
    """args is a tuple of tkinter widgets with .get() methods."""
    data = tuple(widget.get() for widget in args)

    def decorator(func):
        @functools.wraps(func)
        def decorated():
            return func(*data)
        return decorated

    return decorator


def find_file(name, type_):
    from .interface import JsonInterface
    directory = '{direc}/{name}'
    location = type_.split(sep='.')
    if location[0] == '':
        # Leading . indicates name of object is included in path
        location[0] = sanitize_filename(name)
    filename = directory.format(
        direc=location[-1], name='.'.join(location))
    try:
        iface = JsonInterface(filename)
        return iface
    except FileNotFoundError:
        raise


def path_follower(path, alltheway=False):
    from .interface import JsonInterface
    match = re.match(r'/*(\w*.*\.[a-z]*)(/.*)', path)
    try:
        tofile = match.group(1)
        infile = match.group(2)
    except IndexError:
        raise ValueError('Needs to be given as a path to a file then within'
                         'the file to the desired data')
    if (JsonInterface.OBJECTSPATH / tofile).is_file():
        jf = JsonInterface(tofile)
        if alltheway:
            # The data within the sought file
            return jf.get(infile)
        else:
            # The file and path within the file separately, to work with
            #   classes.Resource
            return jf, infile
    else:
        raise FileNotFoundError


def cache(f):
    """Decorator that caches the result of a function."""
    f.__cache = {}

    @functools.wraps(f)
    def cached(*args, **kwargs):
        ret = f(*args, **kwargs)
        f.__cache[(args, tuple(sorted(kwargs.items())))] = ret
        return ret

    return cached


@cache
def get_conditions():
    d = os.path.dirname(os.path.abspath(__file__))
    with open(d + '/conditions.json') as f:
        return json.load(f)


def with_data(data):
    def decorator(f):
        f.__data = data

        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapped

    return decorator
