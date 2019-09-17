from typing import Set

import exceptionsLib as ex
from characterLib import Character
from interface import JsonInterface


class Spell:
    def __init__(self, jf: JsonInterface):
        self.record = jf
        self.name: str = jf.get('/name')
        self.level: int = jf.get('/level')
        self.effect: str = jf.get('/effect')
        self.classes: Set[str] = set(jf.get('/class'))
        self.castingTime: str = jf.get('/casting_time')
        self.duration: str = jf.get('/duration')
        self.range: str = jf.get('/range')
        self.components: str = jf.get('/components')
        self.school: str = jf.get('/school')
        self.isRitual: bool = jf.get('/ritual')
        self.isConcentration: bool = jf.get('/concentration')

    def __eq__(self, other):
        if isinstance(other, Spell):
            return self.record is other.record
        elif isinstance(other, str):
            return self.name == other
        else:
            return False

    def is_available(self, character: Character):
        available = character.classes.spells_available
        names = set(available[self.level])
        both = names & self.classes
        return len(both) > 0


class OwnedSpell(Spell):
    def __init__(self, jf: JsonInterface, owner: Character):
        super().__init__(jf)
        self.owner = owner

    def cast(self) -> str:
        if self.level > 0:
            self.owner.spellPower.cast(self.level)
        return self.effect

    def ritual_cast(self) -> str:
        if not self.isRitual:
            raise ex.NotARitualError()
        return self.effect
