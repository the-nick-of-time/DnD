import re


def modifier(score):
    return (score-10) // 2


def shorten(effect):
    """Takes an effects string and returns the first sentence."""
    if (effect):
        return re.match('^.*?\.', effect).group()
    else:
        return ""
