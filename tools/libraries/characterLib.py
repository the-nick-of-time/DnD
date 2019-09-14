import abilitiesLib as abil
import classLib as cl
from hpLib import HP
from interface import JSONInterface
from raceLib import Race
from settingsLib import Settings


class Character:
    def __init__(self, jf: JSONInterface):
        self.record = jf
        # settings initialization has to happen first, as several things
        # depend on it
        self.settings = Settings(jf.cd('/SETTINGS'))
        self.abilities = abil.Abilities(jf.cd("/abilities"))
        self.race = Race(jf.cd("/race"))
        self.classes = cl.Classes(jf.cd("/classes"), self)
        self.hp = HP(self)
