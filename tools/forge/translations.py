def abbreviate(abil, shouty=True):
    m = {'strength': 'STR', 'dexterity': 'DEX', 'constitution':'CON', 'intelligence': 'INT', 'wisdom': 'WIS', 'charisma': 'CHA'}
    out = m[abil.lower()]
    if(not shouty):
        out = out.lower()
    return out