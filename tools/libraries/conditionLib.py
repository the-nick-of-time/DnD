from typing import List, Union

import exceptionsLib as ex
import helpers as h
from characterLib import Character
from interface import JsonInterface


class Conditions:
    def __init__(self, jf: JsonInterface, character: Character):
        self.record = jf
        self.owner = character
        defs = h.get_conditions()
        self.items = {}
        for name, description in defs.items():
            if name == 'exhaustion':
                self.items[name] = Exhaustion(name, description)
            else:
                self.items[name] = Condition(name, description)
        self.active = set()
        for name in jf.get('/'):
            self.add(name)

    def __str__(self):
        descriptions = [condition.describe()
                        for condition in self.items.values()
                        if condition.active]
        descriptions.sort()
        return '\n'.join(descriptions)

    def __iter__(self):
        yield from self.items.values()

    def add(self, name: str):
        self.items[name].add()

    def remove(self, name: str):
        self.items[name].remove()


class Condition:
    def __init__(self, name: str, description: Union[str, List[str]]):
        self.name = name
        self.description = description
        self.active = False

    def __hash__(self):
        return hash(self.describe())

    def describe(self) -> str:
        return self.description

    def add(self):
        self.active = True

    def remove(self):
        self.active = False


class Exhaustion(Condition):
    def __init__(self, name: str, description: List[str]):
        super().__init__(name, description)
        self.level = 0

    def describe(self) -> str:
        return self.description[self.level - 1]

    def add(self):
        self.level += 1
        self.active = True
        if self.level >= 6:
            raise ex.CharacterDead()

    def remove(self):
        if self.level > 0:
            self.level -= 1
        self.active = bool(self.level)
