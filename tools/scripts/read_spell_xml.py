import json
import re
from pathlib import Path
from typing import List, Tuple, Optional

from bs4 import BeautifulSoup, Tag

from DnD.modules.lib.helpers import sanitize_filename


def parse_one(elem: Tag) -> dict:
    data = {
        'name': elem.find('name').text.rstrip('()ESCAG '),
        'level': int(elem.level.text),
        'school': parse_school(elem.school.text),
        'casting_time': elem.time.text,
        'range': elem.range.text,
        'components': elem.components.text,
        'duration': elem.duration.text,
        'class': parse_classes(elem.classes.text),
        'effect': parse_body(elem('text'))[0],
        'higher_levels': parse_body(elem('text'))[1],

        'ritual': elem.ritual.text == 'YES' if elem.ritual else False,
        'concentration': 'concentration' in elem.duration.text.lower(),
    }
    attack = construct_attack(data['effect'], data['range'])
    if attack:
        data.update(attack)
    return data


def parse_classes(classes: str) -> list:
    names = re.findall(r"(\w+)(?:\s*\(([\w\s]+)\))?", classes)
    return [
        {
            "class": spec[0],
            "subclass": spec[1],
        }
        if spec[1] else
        {
            "class": spec[0]
        }
        for spec in names
    ]


def parse_school(school: str) -> str:
    mapping = {
        'A': 'Abjuration',
        'N': 'Necromancy',
        'C': 'Conjuration',
        'EV': 'Evocation',
        'D': 'Divination',
        'T': 'Transmutation',
        'EN': 'Enchantment',
        'I': 'Illusion',
    }
    return mapping[school]


def parse_body(body: List[Tag]) -> Tuple[str, str]:
    effect = []
    variants = []
    for segment in body:
        if segment.text.startswith('At Higher Levels'):
            variants.append(segment.text)
        else:
            effect.append(segment.text)
    return '\n'.join(effect), '\n'.join(variants)


def construct_attack(body: str, range: str) -> Optional[dict]:
    damage = re.search(r'(\d+d\d+(?:[+-]\d+)?) (\w+) damage', body)
    save = re.search(r'(\w+) saving throw', body, re.IGNORECASE)
    attack = 'spell attack' in body
    if not ((attack or save) and damage):
        return None
    # Try it as the most basic kind of attack
    return {
        "attacks": [
            {
                "range": range,
                "to_hit": {
                    "test": "ATTACKROLL" if attack else "SAVE",
                    "against": "AC" if attack else save.group(1).title(),
                },
                "on_hit": {
                    "damage": {
                        "base_roll": damage.group(1),
                        "damage_type": damage.group(2)
                    }
                }
            }
        ]
    }


def write_one(data: dict, outputdir: Path):
    file = outputdir / sanitize_filename(data['name'] + '.spell')
    with file.open('w') as out:
        json.dump(data, out, indent=2)


def main(filename: Path, outputdir: Path):
    with filename.open('r') as f:
        document = BeautifulSoup(f, 'lxml')
        for spell in document('spell'):
            write_one(parse_one(spell), outputdir)


if __name__ == '__main__':
    inputdir = Path('../../../DnDAppFiles/Compendiums/Spells Compendium.xml')
    outputdir = Path('../../DnD/objects/spell')
    main(inputdir, outputdir)
