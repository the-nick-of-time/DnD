import re

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
        self.skills = set(jf.get('/skills'))
        self.saves = self.classes.saveProficiencies
        self.deathSaveFailures = 0

    @property
    def proficiency(self):
        return self.classes.proficiency

    def ability_check(self, which: abil.AbilityName, skill='', adv=False, dis=False):
        roll = h.d20_roll(adv, dis, self.bonuses.get('lucky', False))
        roll += d.compile(self.abilities[which].modifier)
        if skill in self.skills:
            roll += d.compile(self.proficiency)
            skillBonus = self.bonuses.get('skill_' + skill)
            if skillBonus:
                roll += d.compile(self.parse_vars(skillBonus))
        elif self.bonuses.get('jack_of_all_trades', False):
            roll += d.compile(self.proficiency // 2)
        abilityBonus = self.bonuses.get('check_' + which.value)
        if abilityBonus:
            roll += d.compile(self.parse_vars(abilityBonus))
        return d.verbose(roll)

    def ability_save(self, which: abil.AbilityName, adv=False, dis=False):
        roll = h.d20_roll(adv, dis, self.bonuses.get('lucky', False))
        roll += d.compile(self.abilities[which].modifier)
        if which in self.saves:
            roll += d.compile(self.proficiency)
        abilityBonus = self.bonuses.get('save_' + which.value)
        if abilityBonus:
            roll += d.compile(self.parse_vars(abilityBonus))
        return d.verbose(roll)

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

    def parse_vars(self, varstring):
        if isinstance(varstring, str):
            return re.sub(r'\$([a-zA-Z_]+)',
                          lambda m: self.__match_variable(m.group(1)),
                          varstring)
        elif isinstance(varstring, int) or varstring is None:
            return varstring
        # Recursively evaluate collections (lists, tuples, dicts)
        elif isinstance(varstring, (list, tuple)):
            for i, item in enumerate(varstring):
                varstring[i] = self.parse_vars(item)
        elif isinstance(varstring, dict):
            for key in varstring:
                varstring[key] = self.parse_vars(varstring[key])
            return varstring
        else:
            raise TypeError('This should work on anything directly grabbed '
                            'from an object file')

    def __match_variable(self, key: str):
        if re.match(r'str(ength)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities[abil.AbilityName.STR])
        if re.match(r'dex(terity)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities[abil.AbilityName.DEX])
        if re.match(r'con(stitution)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities[abil.AbilityName.CON])
        if re.match(r'int(elligence)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities[abil.AbilityName.INT])
        if re.match(r'wis(dom)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities[abil.AbilityName.WIS])
        if re.match(r'cha(risma)?_mod(ifier)?', key, flags=re.I):
            return self.abilities[abil.AbilityName.CHA].modifier
        if key.lower() == 'caster_level':
            return self.classes.casterLevel
        if re.match(r'prof(iciency)?', key, flags=re.I):
            return self.proficiency
        if key.lower() == 'level':
            return self.classes.level
        if key.endswith('_level'):
            head, _, _ = key.partition('_')
            try:
                cl = self.classes[head.capitalize()]
            except KeyError:
                return 0
            return cl.level
        raise KeyError('Variable not found')

    def write(self):
        self.record.set('/SETTINGS', self.settings.serialize())
        self.record.write()
