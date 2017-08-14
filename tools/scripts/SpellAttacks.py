import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import interface as iface
import helpers as h

iface.JSONInterface.OBJECTSPATH = '../objects/'

# roll_pattern = '(\d+d\d+)\s?\+?\s?\d*'
# # roll_pattern = '(\d+d\d+)'
# damage_roll_pattern = roll_pattern + ' (\w+) damage'
# saving_throw_pattern = '(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw'
# attack_flag_pattern = 'spell attack'
component_pattern = '(V)?(S)?(M)?(gp)?'

# In the end, needs to set:
# /damage to damage dice
# /attacks to expected number of attacks
#


for f in os.scandir('../objects/spell/'):
    print(f.name)
    jf = iface.JSONInterface('spell/' + f.name)
    # eff = jf.get('/effect')
    # attackroll = re.search(attack_flag_pattern, eff) is not None
    # if (attackroll):
    #     jf.set('/attack_roll', attackroll)
    # else:
    #     save = re.search(saving_throw_pattern, eff)
    #     if (save is not None):
    #         jf.set('/save', save.group(1))
    # damageroll = re.search(damage_roll_pattern, eff)
    # if (damageroll is not None):
    #     jf.set('/damage', damageroll.group(1))
    #     jf.set('/damage_type', damageroll.group(2))
    # else:
    #     roll = re.search(roll_pattern, eff)
    #     if roll:
    #         jf.set('/damage', roll.group(1))
    # jf.write()
    # comp = jf.get('/components')
    # result = re.fullmatch(component_pattern, comp)
    # if (result is not None):
    #     new = []
    #     for item in result.groups():
    #         if (item):
    #             new.append(item)
    #     # result = ((item if item) for item in result.groups())
    #     newcomp = ', '.join(new)
    #     print(newcomp)
    #     jf.set('/components', newcomp)
    #     jf.write()
    desc = jf.get('/effect')
    # new = re.sub('\n(?=[\n$])')
    new = desc.replace('\n\n', '\n').rstrip()
    if (f.name == 'Scrying.spell'):
        print(new)
    jf.set('/effect', new)
    jf.write()
