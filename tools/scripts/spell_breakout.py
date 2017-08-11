import json
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libraries')

from read_md import read_markdown
from helpers import clean

dest = r'C:\Users\Nicholas\Documents\GitHub\DnD\tools\objects\spell\\'
with open(r'C:\Users\Nicholas\Documents\GitHub\DnD\tools\objects\spell_data.json') as base, open(r'C:\Users\Nicholas\Documents\GitHub\DnD\tools\objects\spells.json') as det:
    rollregex = re.compile('([0-9+]+d[0-9+]+)')
    saveregex = re.compile('([DWCSI][a-z]+) saving throw')
    damagetyperegex = re.compile('([a-z]+) damage')
    basedata = json.load(base)
    details = json.load(det)
    grimoire = {}
    for (dirpath, dirnames, filenames) in os.walk(r'C:\Users\Nicholas\Documents\GitHub\grimoire\_posts\\'):
        for name in filenames:
            loaded = read_markdown(dirpath + name)
            entry = {loaded['title'].strip(): loaded['effect']}
            # print(entry)
            grimoire.update(entry)
    for name, defn in basedata.items():
        print(name)
        try:
            detailedentry = details[name]
        except KeyError:
            detailedentry = {'components': defn['components'], 'effect': '', 'range': defn['range']}
        defn['components'] = detailedentry['components']
        defn['effect'] = grimoire[name]
        defn['range'] = detailedentry['range']
        with open(dest + clean(name) + '.spell', 'w') as f:
            json.dump(defn, f, indent=2)
