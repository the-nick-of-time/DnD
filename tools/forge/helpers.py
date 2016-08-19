import re


def modifier(score):
    return (score - 10) // 2


def shorten(effect):
    """Takes an effects string and returns the first sentence."""
    if (effect):
        return re.match('^.*?\.', effect).group()
    else:
        return ""


def clean(name):
    return name.replace(' ', '_').replace('\'', '-')


def unclean(name):
    return name.replace('_', ' ').replace('-', '\'')


def pull_from(*args):
    """args is a tuple of tkinter widgets with .get() methods."""
    data = tuple(widget.get() for widget in args)
    def decorator(func):
        def decorated():
            return func(*data)
        decorated.__name__ = func.__name__
        return decorated
    return decorator
