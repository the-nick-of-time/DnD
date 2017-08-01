import json
import helpers as h

path = '../objects/treasure/'

with open(path + 'gem.treasure', 'r') as infile:
    data = json.load(infile)

for (name, item) in data.items():
    with open(path + h.clean(name).lower() + '.treasure', 'w') as outfile:
        json.dump(item, outfile, indent=2)
