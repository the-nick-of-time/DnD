import json

def clean(name):
    return name.replace(' ', '_').replace('\'', '-').replace('/', '&')

dest = r'C:\Users\Nicholas\Documents\GitHub\DnD\tools\objects\spell\\'
with open(r'C:\Users\Nicholas\Documents\GitHub\DnD\tools\objects\spell_data.json') as base, open(r'C:\Users\Nicholas\Documents\GitHub\DnD\tools\objects\spells.json') as det:
    basedata = json.load(base)
    details = json.load(det)
    for name, defn in basedata.items():
        try:
            detailedentry = details[name]
        except KeyError:
            detailedentry = {'components': defn['components'], 'description': '', 'range': defn['range']}
        defn['components'] = detailedentry['components']
        defn['description'] = detailedentry['description']
        defn['range'] = detailedentry['range']
        with open(dest + clean(name) + '.spell', 'w') as f:
            json.dump(defn, f, indent=2)
