import re


def modifier(score):
    return (score - 10) // 2


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
        "armor": {"magic": MagicArmor,
                  "": Armor},
        "character": {"": Character},
        "class": {"": Class},
        "item": {"magic": MagicItem,
                 "": Item},
        "race": {"": Race},
        "skill": {"": Skill},
        "spell": {"": Spell},
        "treasure": {"": Item},
        "weapon": {
            "magic": {"ranged": MagicRangedWeapon,
                      "": MagicWeapon},
            "ranged": {"magic": MagicRangedWeapon,
                       "": RangedWeapon},
            "": Weapon
        }
    }
    steps = extension.split('.')
    steps[0] = ''  # We don't care about the initial name, even if given
    location = tree
    for step in reversed(steps):
        location = location[step]
    return location
