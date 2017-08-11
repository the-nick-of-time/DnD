import os
import json

from interface import JSONInterface
import helpers as h

JSONInterface.OBJECTSPATH = '../objects/'

with open('../objects/5e-SRD-Monsters.json', 'r') as infile:
    core = json.load(infile)


for monster in core[:-1]:
    print(monster['name'])
    data = {
        "name": monster['name'],
        "AC": monster['armor_class'],
        "HP": monster['hit_dice'],
        "abilities": {
            "Strength": monster['strength'],
            "Dexterity": monster['dexterity'],
            "Constitution": monster['constitution'],
            "Intelligence": monster['intelligence'],
            "Wisdom": monster['wisdom'],
            "Charisma": monster['charisma']
        }
    }
    # TODO: add in skills after implementing that in monsters.py
    # s = json.dumps(data, indent=2)
    # print(s)
    formatstr = '{}monster/{}.monster'
    filename = formatstr.format(JSONInterface.OBJECTSPATH,
                                h.clean(monster['name']))
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=2)
