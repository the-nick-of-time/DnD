import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

import interface as iface
import classes as c
import classmap as cm

iface.JsonInterface.OBJECTSPATH = Path('../objects/')

cleric = iface.JsonInterface('class/Cleric.class')
all = iface.JsonInterface('class/ALL.super.class')
caster = iface.JsonInterface('class/CASTER.super.class')

combined = all + caster + cleric

print(combined.get('ALL/proficiency/0/0'))
print(combined.get('/proficiency/0/0'))
print(combined.get('CASTER/slots/full/12'))
print(combined.get('/slots/full/12'))

jf = iface.JsonInterface('character/Calan.character')
classes = cm.ClassMap(jf.get('/level'))
print(classes.sum())

for n, cl, lv in classes:
    print(cl)

Calan = c.Character(jf)

print(Calan.proficiency)
print(Calan.caster_level)
print(Calan.max_slots)

Berndus = c.Character(iface.JsonInterface('character/Berndus.character'))
print(Berndus.proficiency)
print(Berndus.caster_level)
