import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag

from DnD.modules.lib.helpers import sanitize_filename


class DummyMatch:
    def group(self, num):
        return ''


def parse_one(elem: Tag) -> dict:
    return {
        'name': elem.find('name').text,
        'alignment': elem.alignment.text if elem.alignment else None,
        'AC': int(elem.ac.text.split()[0]),
        'HP': (re.search(r"\((.*)\)", elem.hp.text) or DummyMatch()).group(1),
        'abilities': {
            'Strength': int(elem.str.text),
            'Dexterity': int(elem.dex.text),
            'Constitution': int(elem.con.text),
            'Intelligence': int(elem.int.text),
            'Wisdom': int(elem.wis.text),
            'Charisma': int(elem.cha.text),
        },
        'saves': parse_saves(elem.save.text) if elem.save else [],
        'skills': parse_skills(elem.skill.text) if elem.skill else [],
        'resistances': elem.resist.text if elem.resist else None,
        'vulnerabilities': elem.vulnerable.text if elem.vulnerable else None,
        'immunities': elem.immune.text if elem.immune else None,
        'condition immunities': elem.conditionImmune.text if elem.conditionImmune else None,
        'senses': elem.senses.text if elem.senses else None,
        'passive perception': int(elem.passive.text.split()[-1]) if elem.passive else None,
        'language': elem.languages.text if elem.languages else None,
        # On load this should be hooked into a fractions.Fraction
        'CR': elem.cr.text,
        # TODO: traits and actions?
    }


def parse_saves(text: str) -> list:
    saves = re.findall(r'(\w+)\s+([+-]?\d+)', text)
    mapper = {
        'Str': 'Strength',
        'Dex': 'Dexterity',
        'Con': 'Constitution',
        'Int': 'Intelligence',
        'Wis': 'Wisdom',
        'Cha': 'Charisma',
        'Strength': 'Strength',
        'Dexterity': 'Dexterity',
        'Constitution': 'Constitution',
        'Intelligence': 'Intelligence',
        'Wisdom': 'Wisdom',
        'Charisma': 'Charisma',
    }
    return [{mapper[save[0]]: int(save[1])} for save in saves]


def parse_skills(text: str) -> list:
    skills = re.findall(r'([\w\s]+?) ([+-]?\d+)', text)
    return [{skill[0]: int(skill[1])} for skill in skills]


def write_one(data: dict, outputdir: Path):
    file = outputdir / sanitize_filename(data['name'] + '.monster')
    with file.open('w') as out:
        json.dump(data, out, indent=2)


def main(inputdir: Path, outputdir: Path):
    for filename in inputdir.glob('*'):
        print('Processing ' + filename.name)
        with filename.open('r') as f:
            document = BeautifulSoup(f, 'lxml')
            for monster in document('monster'):
                write_one(parse_one(monster), outputdir)


if __name__ == '__main__':
    inputdir = Path('../../../DnDAppFiles/Bestiary')
    outputdir = Path('../../DnD/objects/monster')
    # main(inputdir, outputdir)
    main(Path('../../../DnDAppFiles/Homebrew & Third Party/Monsters'), outputdir)
