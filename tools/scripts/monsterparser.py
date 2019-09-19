import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

from interface import JsonInterface

JsonInterface.OBJECTSPATH = Path('../objects/')

monster = {}
dry = False
# t = ElementTree.parse("../objects/Volo's Bestiary.xml")
# t = ElementTree.parse("../../../DnDAppFiles/Bestiary/Curse of Strahd Bestiary.xml")
# t = ElementTree.parse("../../../DnDAppFiles/Bestiary/Hoard of the Dragon Queen Bestiary.xml")
# t = ElementTree.parse("../../../DnDAppFiles/Bestiary/Out of the Abyss.xml")
# t = ElementTree.parse("../../../DnDAppFiles/Bestiary/Phandelver Bestiary.xml")
# t = ElementTree.parse("../../../DnDAppFiles/Bestiary/Princes of the Apocalypse Bestiary.xml")
# t = ElementTree.parse("../../../DnDAppFiles/Bestiary/Storm King's Thunder.xml")
# t = ElementTree.parse("../../../DnDAppFiles/Bestiary/Tales From the Yawining Portal Bestiary.xml")
# t = ElementTree.parse("../../../DnDAppFiles/Bestiary/The Rise of Tiamat Bestiary.xml")


# root = t.getroot()
# for item in root:
#     # print(item[0].text)
#     monster['name'] = item[0].text
#     # print(item[4].text)
#     monster['armor_class'] = item[4].text
#     # print(item[5].text)
#     s = item[5].text
#     m = re.search('\(.+\)', s).group(0).strip('()')
#     monster['hit_dice'] = m
#     for name, abil in zip(['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'], item[7:13]):
#         # print(abil.text)
#         monster[name] = int(abil.text)
    # print(monster)
    # for child in item:
    #     print(child.text)

# with open('../objects/5e-SRD-Monsters.json', 'r') as infile:
#     core = json.load(infile)
#
#
# for monster in core[:-1]:
#     print(monster['name'])
#     data = {
#         "name": monster['name'],
#         "AC": monster['armor_class'],
#         "HP": monster['hit_dice'],
#         "abilities": {
#             "Strength": monster['strength'],
#             "Dexterity": monster['dexterity'],
#             "Constitution": monster['constitution'],
#             "Intelligence": monster['intelligence'],
#             "Wisdom": monster['wisdom'],
#             "Charisma": monster['charisma']
#         }
#     }
#     # print(data)
#     # TODO: add in skills after implementing that in monsters.py
#     if dry:
#         s = json.dumps(data, indent=2)
#         print(s)
#     else:
#         formatstr = '{}monster/{}.monster'
#         filename = formatstr.format(JsonInterface.OBJECTSPATH,
#                                     h.clean(monster['name']))
#         with open(filename, 'w') as outfile:
#             json.dump(data, outfile, indent=2)


for f in os.scandir(JsonInterface.OBJECTSPATH / 'monster/'):
    print(f.name)
    jf = JsonInterface('monster/' + f.name)
    ac = jf.get('/AC')
    if isinstance(ac, str):
        new = re.match('\d+', ac)
        if new is not None:
            jf.set('/AC', int(new.group(0)))
    jf.write()
