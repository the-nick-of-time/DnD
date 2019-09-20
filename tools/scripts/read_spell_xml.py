import json
import re
from pathlib import Path
from typing import List, Tuple

from bs4 import BeautifulSoup, Tag

from DnD.modules.lib.helpers import sanitize_filename


def parse_one(elem: Tag) -> dict:
    return {
        'name': elem.find('name').text.rstrip('()E '),
        'level': int(elem.level.text),
        'school': elem.school.text,
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


def parse_classes(classes: str) -> list:
    names = re.findall(r"(\w+)(?:\s*\(([\w\s]+)\))", classes)
    return [
        {
            "class": spec[0],
            "subclass": spec[1],
        }
        if len(spec) > 1 else
        {
            "class": spec[0]
        }
        for spec in names
    ]


def parse_body(body: List[Tag]) -> Tuple[str, str]:
    effect = []
    variants = []
    for segment in body:
        if segment.text.startswith('At Higher Levels'):
            variants.append(segment.text)
        else:
            effect.append(segment.text)
    return '\n'.join(effect), '\n'.join(variants)


def write_one(data: dict, outputdir: Path):
    file = outputdir / sanitize_filename(data['name'] + '.spell')
    with file.open('w') as out:
        json.dump(data, out, indent=2)


def main(filename: Path, outputdir: Path):
    with filename.open('r') as f:
        document = BeautifulSoup(f, 'lxml-xml')
        for spell in document('spell'):
            write_one(parse_one(spell), outputdir)


if __name__ == '__main__':
    inputdir = Path('../../../DnDAppFiles/Compendiums/Spells Compendium.xml')
    outputdir = Path('../../DnD/objects/spell')
    main(inputdir, outputdir)
