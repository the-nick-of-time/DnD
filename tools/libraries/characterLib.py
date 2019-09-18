import dndice as d

import abilitiesLib as abil
import bonusLib as bonus
import classLib as classes
import exceptionsLib as ex
import helpers as h
import hpLib as hp
import raceLib as race
import settingsLib as settings
import spellcastingLib as casting
from interface import JsonInterface


class Character:
    def __init__(self, jf: JsonInterface):
        self.record = jf
        # settings initialization has to happen first, as several things
        # depend on it
        self.settings = settings.Settings(jf.cd('/SETTINGS'))
        self.abilities = abil.Abilities(jf.cd("/abilities"))
        self.race = race.Race(jf.cd("/race"))
        self.classes = classes.Classes(jf.cd("/classes"), self)
        self.hp = hp.HP(jf.cd('/HP'), self)
        if self.settings.spellPoints:
            self.spellPower = casting.SpellPoints(self)
        else:
            self.spellPower = casting.SpellSlots(self)
        self.bonuses = bonus.Bonuses()
        self.deathSaveFailures = 0

    def death_save(self):
        if self.hp.current > 0:
            return ''
        roll = d.basic(h.d20_roll(luck=self.bonuses.get('lucky')))
        if roll == 20:
            self.hp.current = 1
            self.deathSaveFailures = 0
        if roll < 10:
            self.deathSaveFailures += 1
        if roll == 1:
            # add a second failure
            self.deathSaveFailures += 1
        if self.deathSaveFailures >= 3:
            raise ex.CharacterDead()

    def parse_vars(self, string) -> str:
        pass

    def write(self):
        self.record.write()
