import os
import re
from collections import OrderedDict
from functools import wraps
from math import ceil

import dndice as r

import classmap as cm
import helpers as h
import interface as iface
from exceptionsLib import OutOfSpells, OutOfItems, LowOnResource
from settingsLib import Settings


class Class:
    """Nonspecific representation of a D&D class.

    Data:
    name: The name of the class
    level: The level you have in this class

    Methods:
    get: Get from the LinkedInterface that this class reads from
    """

    def __init__(self, jf, classlevel):
        self.record = jf
        self.name = jf.get('/name')
        self.level = classlevel
        self.hit_dice = jf.get('/hit_dice')

    def get(self, key):
        return self.record.get(key)


class Race:
    """Representation of a race.

    Data:
    name: The name of this race
    features: The features associated with this race
    """

    def __init__(self, jf, name):
        self.record = jf
        self.name = name
        self.features = self.get_features()

    def get_features(self):
        featuredict = self.record.get('*/features')
        return featuredict


class Resource:
    """A resource with an associated value and recharge

    Data:
    number: The number of the resource that you currently have. Found in the
        character file.
    maxnumber: The maximum number of the resource that you can have. Often
        found in a separate file from the character. If you set it explicitly
        at any time, it is written into the character file and will override
        any other definition of the maximum number.
    value: The number you get when you use a resource. This can be a number
        or a roll. For instance, a hit die obviously has a single die as its
        value.

    Methods:
    use: Use some number of resources if you have that number remaining. Return
        the total roll.
    regain: Regain some number of resources, up to the maximum.
    rest: Takes the length of rest (short, long, or turn) and resets the number
        to the maximum number if the rest was long enough.
    reset: Resets the number to the maximum number. (Generally you want to use
        the rest interface rather than explicit reset though.)
    write: Write the major record; most often a character file. (Generally use
        Character.write if possible.)
    """

    def __init__(self, jf, path, defjf=None, defpath=None, character=None):
        self.record = jf
        self.character = character
        self.definition = defjf if (defjf is not None) else jf
        self.path = path
        self.defpath = defpath if (defpath is not None) else path
        self.name = self.definition.get(self.defpath + '/name')
        # self.value = self.definition.get(self.defpath + '/value')
        v = self.definition.get(self.defpath + '/value')
        if self.character is not None:
            val = self.character.parse_vars(v, mathIt=False)
            if isinstance(val, str):
                pattern = r'\(.*\)'
                rep = lambda m: str(r.basic(m.group(0)))
                new = re.sub(pattern, rep, val)
                self.value = new
            else:
                self.value = val
        else:
            self.value = v
        self.recharge = self.definition.get(self.defpath + '/recharge')

    @property
    def number(self):
        return self.record.get(self.path + '/number')

    @number.setter
    def number(self, value):
        self.record.set(self.path + '/number', value)

    @property
    def maxnumber(self):
        val = self.record.get(self.path + '/maxnumber')
        if val is not None:
            if self.character is not None:
                return self.character.parse_vars(val)
            return val
        if self.character is not None:
            mx = self.definition.get(self.defpath + '/maxnumber')
            return self.character.parse_vars(mx)
        return self.definition.get(self.defpath + '/maxnumber')

    @maxnumber.setter
    def maxnumber(self, value):
        self.record.set(self.path + '/maxnumber', value)

    def use(self, howmany):
        if self.number < howmany:
            raise LowOnResource(self)
        self.number -= howmany
        if isinstance(self.value, str):
            return r.basic('+'.join([self.value] * howmany))
        elif isinstance(self.value, int):
            return howmany * self.value
        else:
            return 0

    def regain(self, howmany):
        if self.number + howmany > self.maxnumber:
            self.reset()
        else:
            self.number += howmany

    def reset(self):
        self.number = self.maxnumber

    def rest(self, what):
        if what == 'long':
            self.reset()
            return self.number
        if what == 'short':
            if self.recharge == 'short rest' or self.recharge == 'turn':
                self.reset()
                return self.number
        if what == 'turn':
            if self.recharge == 'turn':
                self.reset()
                return self.number
        return -1

    def write(self):
        self.record.write()


class Feature:
    """Represents a feature from a class or race.

    Data:
    bonuses: Any bonuses that might be conferred by the feature.
    resource: Any resource that might be provided by the feature.
    name: The name of the feature.
    """

    def __init__(self, char, path):
        # char is the Character
        # path is a full path to the feature including its file
        tup = h.path_follower(path)
        self.character = char
        self.charRecord = char.record
        self.record = tup[0]
        self.path = tup[1]
        self.bonuses = self.record.get(self.path + '/bonus')
        rs = self.record.get(self.path + '/resource')
        if rs is not None:
            name = rs['name']
            if self.charRecord.get('/resources/' + name) is None:
                # newly gained, not yet registered in the character file
                if self.charRecord.get('/resources') is None:
                    self.charRecord.set('/resources', {})
                self.charRecord.set('/resources/' + name, {'number': 0})
            self.resource = Resource(self.charRecord, '/resources/' + name,
                                     self.record, self.path + '/resource',
                                     self.character)
        else:
            self.resource = rs

    def __str__(self):
        return self.record.get(self.path + '/description')

    @property
    def name(self):
        return self.path.split('/')[-1]


class Character:
    """Represents a PC or NPC.

    Data:
    name: The name of the character.
    classes: A ClassMap object of the total class levels that your character
        has.
    race: A RaceMap object of the race of the character.
    level: The total level of the character.
    caster_level: The total caster level of the character.
    abilities: A dictionary mapping ability names to scores.
    inventory: An Inventory object containing everything that you are carrying.
    AC: The current AC of the character.
    proficiency: The proficiency bonus of the character.
    hp: A HPHandler object that deals with the character's HP and also HD.
    skills: A list of skill names in which you are proficient.
    saves: A list of ability saves in which you are proficient.
    features: A list of Feature objects that detail the features found in your
        character file.
    bonuses: A dict of bonuses organized as applicability: value.
    spells: A SpellsPrepared object detailing all the spells that you currently
        have prepared.
    attacks: A dict mapping names of weapons or spells to the relevant Attack
        objects.
    resources: A list of Resource objects, detailing resources gained from
        class or race features, or from equipped items.
    conditions: A set of conditions that are currently active on you.
    cantrip_scale: An integer of how many times you should roll cantrip damage
        dice (as it scales with your level).
    spell_slots: A <= 10-element list of numbers where the number at a certain
        index is the number of spell slots that you have remaining. At 0th
        level (cantrips) it should always be 999999.
    max_spell_slots: A <= 10-element list of numbers where the number at a
        certain index is the maximum number of spell slots available to you.

    Methods:
    get: Gets a value from the character file interface.
    set: Directly sets a value in the character file interface.
    add_condition: Adds a condition to what the character currently has.
    remove_condition: Removes a condition from the character.
    spell_spend: Given a Spell, spends an appropriate spell slot. On failure,
        raises OutOfSpells.
    item_consume: Given an item name, tries to deduct that item from the
        current inventory.
    ability_check: Rolls an ability check, given advantage, disadvantage, and
        optionally what skill is being applied.
    ability_save: Rolls an ability save, given advantage and disadvantage.
    death_save: Rolls a death saving throw. Tracked in self.death_save_fails.
    set_ability: Set an ability score.
    spell_slots_get: Get spell slots left of a given level, or the full list if
        given '*'.
    spell_slots_set: Set current spell slots a given level, or the full list if
        given '*'.
    save_DC: Given a Spell, calculates the save DC against it.
    relevant_abil: Given a Spell or Weapon, returns the ability score that
        applies to the situation. Given multiple options, returns the best one.
    rest: Takes the length of rest (short, long, or turn) and causes the
        relevant resources, HP, and the like to recover.
    parse_vars: Replaces variables plugged into a string (prefixed by $) with
        the values from the character. Important values would be ${abil}_mod,
        $proficiency, ${Class}_level, $level, and $caster_level.
    write: Writes all changes to the file.
    """
    PROFICIENCY_DICE = False
    # Options:
    #   'fast': regain all HD on long rest
    #   'vanilla': regain all HP and half HD on long rest
    #   'slow': regain half HD on long rest
    HEALING = 'vanilla'

    def __init__(self, jf):
        self.record = jf
        self.name = jf.get('/name')
        self.abilities = jf.get('/abilities')
        self.skills = jf.get('/skills')
        self.saves = jf.get('/saves')
        lv = jf.get('/level')
        self.classes = cm.ClassMap(lv)
        self.race = cm.RaceMap(jf.get('/race'))
        self.hp = HPHandler(self.record)
        self.inventory = Inventory(self.record)
        self.features = self.get_features()
        self.bonuses = self.get_bonuses()
        self.spells = SpellsPrepared(jf, self)
        self.attacks = self.register_attacks()
        self.resources = self.get_resources()
        self.death_save_fails = 0
        self.conditions = set(self.record.get('/conditions') or [])
        Settings.initialize(self.record.get('/SETTINGS'))

    def __str__(self):
        return self.name

    def __getattr__(self, key):
        key = key.lstrip('$')
        if re.match('str(ength)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities['Strength'])
        if re.match('dex(terity)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities['Dexterity'])
        if re.match('con(stitution)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities['Constitution'])
        if re.match('int(elligence)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities['Intelligence'])
        if re.match('wis(dom)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities['Wisdom'])
        if re.match('cha(risma)?_mod(ifier)?', key, flags=re.I):
            return h.modifier(self.abilities['Charisma'])
        if key.lower() == 'caster_level':
            return self.caster_level
        if re.match('prof(iciency)?', key, flags=re.I):
            return self.proficiency
        if key.lower() == 'level':
            return self.level
        if key.endswith('_level'):
            head, _, _ = key.partition('_')
            try:
                cl = self.classes[head.capitalize()]
            except KeyError:
                return 0
            return cl.level
        return self.record.get('/' + key)

    def get(self, key):
        return self.record.get(key)

    def set(self, path, value):
        return self.record.set(path, value)

    def add_condition(self, name):
        if name == 'exhaustion':
            for i in range(6):
                fmt = 'exhaustion{}'
                if fmt.format(i + 1) in self.conditions:
                    self.conditions.remove(fmt.format(i + 1))
                    self.conditions.add(fmt.format(i + 2))
                    return True
            self.conditions.add('exhaustion1')
            return True
        else:
            self.conditions.add(name)
            return True

    def remove_condition(self, name):
        if name == 'exhaustion':
            for i in range(6):
                fmt = 'exhaustion{}'
                if fmt.format(i + 1) in self.conditions:
                    self.conditions.remove(fmt.format(i + 1))
                    if i > 0:
                        self.conditions.add(fmt.format(i))
                    return True
        else:
            try:
                self.conditions.remove(name)
                return True
            except KeyError:
                return False

    def register_attacks(self):
        rv = {}
        for item in self.inventory:
            if isinstance(item.obj, Attack):
                rv[item.name] = item
        for sp in self.spells:
            if isinstance(sp, SpellAttack):
                rv[sp.name] = sp
        return rv

    def spell_spend(self, spell):
        if isinstance(spell, int):
            lv = spell
            path = '/spell_slots/' + str(spell)
        else:
            lv = spell.level
            path = '/spell_slots/' + str(spell.level)
        num = self.record.get(path)
        if num > 0:
            self.record.set(path, num - 1)
        else:
            for val in range(lv, len(self.spell_slots)):
                path = '/spell_slots/' + str(val)
                num = self.record.get(path)
                if num is not None and num > 0:
                    self.record.set(path, num - 1)
                    return None
            # If it fails to find a spell slot, you're out of spells
            raise (OutOfSpells(self, spell))

    def item_consume(self, name):
        if name is not None:
            try:
                obj = self.inventory[name]
            except KeyError:
                raise OutOfItems(self, name)
            if obj.number > 0:
                obj.number -= 1
            else:
                raise OutOfItems(self, name)

    def ability_check(self, which, skill='', adv=False, dis=False):
        applySkill = skill in self.skills
        ability = h.modifier(self.abilities[which])
        rollstr = h.d20_roll(adv, dis, self.bonuses.get('lucky', False))
        roll = r.basic(rollstr)
        if applySkill:
            prof = self.proficiency
        elif self.bonuses.get('jack_of_all_trades', False):
            prof = self.proficiency // 2
        else:
            prof = 0
        bon = (self.parse_vars(self.bonuses.get('check', {}).get(which, 0))
               + self.parse_vars(self.bonuses.get('skill', {}).get(skill, 0)))
        return (roll + prof + ability + bon, prof + ability + bon, roll)

    def ability_save(self, which, adv=False, dis=False):
        applyprof = which in self.saves
        if applyprof:
            prof = self.proficiency
        else:
            prof = 0
        ability = h.modifier(self.abilities[which])
        rollstr = h.d20_roll(adv, dis, self.bonuses.get('lucky', False))
        roll = r.basic(rollstr)
        bon = self.parse_vars(self.bonuses.get('save', {}).get(which, 0))
        return roll + prof + ability + bon, prof + ability + bon, roll

    def death_save(self):
        val = r.basic(h.d20_roll(luck=self.bonuses.get('lucky', False)))
        if val == 1:
            self.death_save_fails += 2
        elif val == 20:
            self.death_save_fails = 0
            self.remove_condition('dying')
            # Signal that you're better now
        elif val < 10:
            self.death_save_fails += 1
        if self.death_save_fails >= 3:
            self.conditions.add('dead')
        return val

    def get_bonuses(self):
        def add_bonus(self, new, bonuses):
            nonstackable = {'base_AC', 'lucky', 'jack_of_all_trades',
                            'attacks'}
            for var, amount in new.items():
                if var not in bonuses:
                    bonuses.update({var: amount})
                elif var in nonstackable:
                    # values are evaluated only at creation time, but should
                    #   hopefully be static
                    newval = self.parse_vars(amount)
                    existing = self.parse_vars(bonuses[var])
                    if newval > existing:
                        bonuses[var] = amount
                else:
                    newval = self.parse_vars(amount)
                    existing = self.parse_vars(bonuses[var])
                    if isinstance(amount, dict):
                        # should only happen for skills?
                        bonuses[var].update(newval)
                    else:
                        bonuses[var] = newval + existing

        bonuses = {}
        for item in self.inventory:
            if item.equipped:
                newbonus = item.get('/bonus')
                if newbonus is not None:
                    add_bonus(self, newbonus, bonuses)
        for f in self.features:
            new = f.bonuses
            if new is not None:
                add_bonus(self, new, bonuses)
        return bonuses

    def get_features(self):
        features = []
        # features = {}
        # features.update(self.race.features)
        # for n, c, l in self.classes:
        #     features.update(c.features)
        for n, p in self.record.get('/features').items():
            # features[n] = Feature(p)
            features.append(Feature(self, p))
        return features

    def get_resources(self):
        resources = []
        for f in self.features:
            if f.resource:
                resources.append(f.resource)
        for item in self.inventory:
            if item.equipped:
                try:
                    res = item.charge
                    definition = res['path']
                    (jf, path) = h.path_follower(definition)
                    new = MagicCharge(self.record, item.path + '/charge',
                                      jf, path)
                    resources.append(new)
                except AttributeError:
                    continue
        return resources

    def set_ability(self, name, value):
        self.abilities[name] = value
        self.record.set('/abilities/' + name, self.abilities[name])

    @property
    def cantrip_scale(self):
        for n, cl, lv in self.classes:
            caster_type = cl.get('/spellcasting/levels')
            if caster_type is None:
                continue
            else:
                path = '/cantrip_damage/{}'.format(self.level - 1)
                return cl.get(path)
        return 1

    @property
    def weapon_prof(self):
        total = []
        for c, lv in self.classes:
            total.extend(c.weapons['types'])
            total.extend(c.weapons['specific'])
        return total

    @property
    def AC(self):
        # It's possible to have a new calculation of base AC in bonuses
        bonusbase = self.bonuses.get('base_AC', 0)
        if bonusbase:
            baseAC = self.parse_vars(bonusbase)
        else:
            baseAC = 10 + self.dex_mod

        bonusAC = self.bonuses.get('AC', 0)
        for item in self.inventory:
            if isinstance(item.obj, Armor):
                if item.equipped:
                    # ac = item.get('/base_AC')
                    ac = item.get_AC(self.dex_mod)
                    baseAC = ac if (ac is not None and ac > baseAC) else baseAC
        return baseAC + bonusAC

    @property
    def level(self):
        return self.classes.sum()

    @property
    def caster_level(self):
        _level = 0
        for n, c, lv in self.classes:
            caster_type = c.get('/spellcasting/levels')
            if caster_type is None:
                continue
            elif caster_type == 'full' or caster_type == 'warlock':
                _level += lv
                continue
            elif caster_type == 'half':
                _level += int(lv / 2)
                continue
            elif caster_type == 'third':
                _level += int(lv / 3)
                continue
        return _level

    @property
    def spell_slots(self):
        return self.record.get('/spell_slots')

    def spell_slots_get(self, level):
        block = self.record.get('/spell_slots')
        if level == '*':
            return block
        return block[level]

    def spell_slots_set(self, level, value):
        if level == '*':
            self.record.set('/spell_slots', value)
        elif isinstance(level, int):
            self.record.set('/spell_slots/' + str(level), value)

    @property
    def max_spell_slots(self):
        # This will fuck up on warlock multiclasses, I think I need to treat
        #   those spell slots as a Resource instead
        cl = self.classes[0]
        if len(self.classes) == 1:
            t = cl.get('/spellcasting/slots')
            if t is None:
                return []
            lv = self.level
        else:
            t = 'full'
            lv = self.caster_level
        path = '/max_spell_slots/{}/{}'.format(t, lv)
        return cl.get(path)

    @property
    def proficiency(self):
        c = self.classes[0]
        val = c.get('/proficiency')[int(self.PROFICIENCY_DICE)][self.level - 1]
        return r.basic(val)

    def save_DC(self, spell):
        return (8
                + self.bonuses.get('save_DC', 0)
                + h.modifier(self.relevant_abil(spell))
                + self.proficiency)

    def relevant_abil(self, forwhat):
        if isinstance(forwhat, Spell):
            sharedclasses = set(forwhat.classes) & set(self.classes.names())
            if sharedclasses:
                # It was actually found in one of your class spell lists
                classnames = sharedclasses
            else:
                # It wasn't, yet you have it nonetheless
                # Just get the largest number from your classes, as I have no
                #   more ways of determining spell source
                classnames = self.classes.names()
            candidate = 0
            for name in classnames:
                abilname = self.classes[name].get('/spellcasting/ability')
                if abilname is not None:
                    score = self.abilities[abilname]
                    if score > candidate:
                        candidate = score
            return candidate

        elif isinstance(forwhat, Weapon):
            candidate = 0
            for abilname in forwhat.ability:
                score = self.abilities[abilname]
                if score > candidate:
                    candidate = score
            return candidate
        else:
            raise TypeError('This must be called with a spell or a weapon.')

    def rest(self, what):
        self.hp.rest(what)
        for res in self.resources:
            res.rest(what)
        if what == 'long':
            self.record.set('/spell_slots', self.max_spell_slots[:])
            self.remove_condition('exhaustion')
        elif what == 'short':
            pass

    def parse_vars(self, s, mathIt=True):
        if isinstance(s, str):
            pattern = r'\$[a-zA-Z_]+'
            new = re.sub(pattern, lambda m: str(self.__getattr__(m.group(0))), s)
            if mathIt:
                return r.basic(new)
            else:
                return new
        elif isinstance(s, (list, tuple)):
            for i, item in enumerate(s):
                s[i] = self.parse_vars(item, mathIt)
            return s
        elif isinstance(s, int) or s is None:
            return s
        elif isinstance(s, dict):
            for n in s:
                s[n] = self.parse_vars(s[n], mathIt)
            return s
        else:
            raise TypeError('This should work on anything directly grabbed '
                            'from an object file')

    def write(self):
        self.record.set('/abilities', self.abilities)
        self.record.set('/conditions', list(self.conditions))
        self.record.set('/level', str(self.classes))
        # self.record.set('/spell_slots', self.spell_slots)
        self.record.write()


class Inventory:
    """Handles the inventory from a character file.

    Data:
    items: A dictionary of name: ItemEntry object.

    Methods:
    __getitem__: Allows treating this object as a dict of ItemEntry objects.
    getq: Given a name, get the number of that item that you have.
    setq: Given a name and new number, sets the number of that item that you
        have.
    newslot: Given name, quantity, item type, and whether it is equipped,
        create a new slot in the inventory for that item.
    """

    def __init__(self, jf):
        """
        Parameters
        ----------
        jf: a JSONInterface to the character file
        """
        self.record = jf
        self.items = {}
        self.load_items()

    def __getitem__(self, name):
        return self.items[name]

    def __iter__(self):
        return (entry for entry in self.items.values())

    def load_items(self):
        for name in self.record.get('/inventory'):
            path = '/inventory/' + name
            self.items[name] = ItemEntry(self.record, path)

    def setq(self, name, value):
        """Sets the quantity of an object."""
        self.items[name].number = value

    def getq(self, name):
        """Gets the number of an object you have.
        Returns
        -------
        number if named item exists, else 0
        """
        return self.items[name].number or 0

    def newslot(self, name, quantity=1, type='item', equipped=False):
        """Creates a new item in the inventory."""
        path = '/inventory/' + name
        self.record.set(path, OrderedDict())
        self.record.set(path + '/type', type)
        self.record.set(path + '/quantity', quantity)
        self.record.set(path + '/equipped', equipped)
        self.load_items()

    def write(self):
        self.record.write()


class ItemEntry:
    """Handles an item as it exists in a character's inventory.

    Data:
    name: The item's name.
    number: How many of the item you have.
    weight: How much one of the item weighs.
    value: How much one of the item is worth, in gp.
    equipped: Where the item is equipped, if anywhere.
    type: The type of the item: weapon, ranged weapon, item, etc.
    consumes: If this item consumes some item when used, it returns that.

    Methods:
    get: Get directly from the object's JSONInterface.
    use: Use the item. Returns a string with the effects of the item.
    describe: Returns the item's description.
    """

    def __init__(self, jf, path, character=None):
        self.record = jf
        self.path = path
        self.person = character
        self.load_from_file()

    def __getattr__(self, key):
        val = self.record.get(self.path + '/' + key)
        if val is not None:
            return val
        if self.obj:
            try:
                return self.obj.__getattribute__(key)
            except AttributeError:
                val = self.obj.__getattr__(key)
                if val is not None:
                    return val
                raise AttributeError
        raise AttributeError

    def load_from_file(self):
        itemtype = self.record.get(self.path + '/type').replace(' ', '.')
        basetype = itemtype.split(sep='.')[-1]
        itemclass = h.type_select('.' + itemtype)
        name = h.clean(self.path.split(sep='/')[-1])
        filename = '{b}/{n}.{t}'.format(b=basetype, t=itemtype, n=name)
        if (os.path.exists(iface.JSONInterface.OBJECTSPATH
                           + filename)):
            jf = iface.JSONInterface(filename)
            self.obj = itemclass(jf)
        else:
            self.obj = None

    @property
    def name(self):
        if self.obj is not None:
            return self.obj.name
        else:
            return self.path.split(sep='/')[-1]

    @property
    def number(self):
        return self.record.get(self.path + '/quantity')

    @number.setter
    def number(self, value):
        if not isinstance(value, int):
            try:
                value = int(value)
            except TypeError as e:
                raise e
        self.record.set(self.path + '/quantity', value)

    @property
    def equipped(self):
        return self.record.get(self.path + '/equipped')

    @equipped.setter
    def equipped(self, value):
        # Make it a str instead for slot name occupied
        self.record.set(self.path + '/equipped', value)
        # if (isinstance(value, bool)):
        #     self.record.set(self.path + '/equipped', value)
        # else:
        #     raise TypeError('The equipped value must be bool')

    @property
    def type(self):
        return self.record.get(self.path + '/type')

    @property
    def weight(self):
        if self.obj is not None:
            return self.obj.weight
        else:
            return 0

    @property
    def value(self):
        if self.obj is not None:
            return self.obj.value
        else:
            return 0

    @property
    def consumes(self):
        if self.obj is not None:
            return self.obj.consumes
        else:
            return None

    def get(self, key):
        if self.obj is not None:
            return self.obj.get(key)
        return None

    def use(self):
        if self.obj is not None:
            return self.obj.use()
        else:
            return ''

    def set_owner(self, character):
        self.person = character
        if self.obj is not None:
            self.obj.set_owner(character)

    def describe(self):
        if self.obj is not None:
            return self.obj.describe()
        else:
            return ''


class HPHandler:
    """Handles the HP and HD from a character file.

    Data:
    hd: A dictionary of the hit dice sizes corresponding to HDHandlers.
    current: How many hit points you currently have.
    max: Your hit point maximum.
    temp: The number of temporary hit points you currently have.

    Methods:
    change_HP: Change your HP by a specified amount. If the amount is negative,
        this is damage.
    temp_HP: Add to your temp HP.
    use_HD: Use a hit die and regain those HP.
    rest: If rest is 'long', reset HP and regain half of all HD.
    write: Write all changes to the file.
    """

    def __init__(self, jf):
        self.record = jf
        self.hd = {size: HDHandler(jf, size) for size in jf.get('/HP/HD')}

    @property
    def current(self):
        return self.record.get('/HP/current')

    @current.setter
    def current(self, value):
        self.record.set('/HP/current', value)

    @property
    def max(self):
        return self.record.get('/HP/max')

    @max.setter
    def max(self, value):
        self.record.set('/HP/max', value)

    @property
    def temp(self):
        return self.record.get('/HP/temp')

    @temp.setter
    def temp(self, value):
        self.record.set('/HP/temp', value)

    def change_HP(self, amount):
        """Changes HP by any valid roll as the amount."""
        delta = r.basic(amount)
        if delta == 0:
            return 0
        # current = self.record.get('/HP/current')
        current = self.current
        if delta < 0:
            # temp = self.record.get('/HP/temp')
            temp = self.temp
            if abs(delta) > temp:
                delta += temp
                temp = 0
                current += delta
                # self.record.set('/HP/temp', temp)
                self.temp = temp
                # self.record.set('/HP/current', current)
                self.current = current
                return delta
            else:
                temp += delta
                # self.record.set('/HP/temp', temp)
                self.temp = temp
                return 0
        else:
            # max_ = self.record.get('/HP/max')
            max_ = self.max
            delta = delta if (current + delta <= max_) else max_ - current
            current += delta
            # self.record.set('/HP/current', current)
            self.current = current
            return delta

    def temp_HP(self, amount):
        """Adds a rollable amount to your temp HP"""
        delta = r.basic(amount)
        if delta == 0:
            return 0
        temp = self.record.get('/HP/temp')
        if delta > temp:
            temp = delta
        self.record.set('/HP/temp', temp)
        return 0

    def use_HD(self, which):
        """Use a specific one of your hit dice."""
        val = self.hd[which].use_HD()
        self.change_HP(val)
        return val

    def rest(self, what):
        if what == 'long':
            # mx = self.record.get('/HP/max')
            # self.record.set('/HP/current', mx)
            if Character.HEALING in ['vanilla', 'fast']:
                self.current = self.max
            self.temp = 0
        for obj in self.hd.values():
            obj.rest(what)

    def write(self):
        for item in self.hd.values():
            item.write()
        self.record.write()


class HDHandler(Resource):
    """Handles one set of hit dice for a character.

    Data:
    As Resource, but with the assumptions made that it recharges on a long
        rest, its name is 'Hit Die', and its value is its size

    Methods:
    use_HD: Returns the result of rolling itself + the character's Constitution
        modifier.
    rest: Overrides Resource.rest, it only regains half of its maximum number
        of HD.
    """

    def __init__(self, jf, size):
        Resource.__init__(self, jf, '/HP/HD/' + size)
        self.name = 'Hit Die'
        self.value = size
        self.recharge = 'long'

    def use_HD(self):
        try:
            roll = self.use(1)
        except LowOnResource:
            return 0
        conmod = h.modifier(self.record.get('/abilities/Constitution'))
        return roll + conmod if (roll + conmod > 1) else 1

    def rest(self, what):
        if what == 'long':
            if Character.HEALING == 'fast':
                self.reset()
            else:
                self.regain(ceil(self.maxnumber / 2))
        if what == 'short':
            if Character.HEALING == 'fast':
                self.regain(ceil(self.maxnumber / 4))


class Attack:
    """Base for other attacks.

    Data:
    damage_dice: The damage dice of this attack.
    num_targets: How many targets can be hit by this attack. If the
        attack is AOE, just use a reasonable upper bound.

    Methods:
    @staticmethod
    display_result: Display the result of an attack.

    attackwrap: This decorator ensures that the attack methods of all
        subclasses are handled correctly.
    """

    def __init__(self, jf):
        self.damage_dice = jf.get('/damage')
        self.num_targets = jf.get('/attacks') or 1

    @staticmethod
    def display_result(result):
        # IMPLEMENTATION: result must be a 3-item iterable made of:
        # an iterable of attack rolls
        # an iterable of damage rolls
        # a string of the effects of the attack
        attack_string = 'Attack rolls: ' + ', '.join(str(a) for a in result[0])
        damage_string = 'Damage rolls: ' + ', '.join(str(a) for a in result[1])
        effects = result[2]
        return attack_string, damage_string, effects

    @staticmethod
    def attackwrap(attack_function):
        @wraps(attack_function)
        def modified(self, character, adv, dis, attack_bonus, damage_bonus):
            # This decorator will be applied to all attack() methods of
            # subclasses of this class. Anything that should apply to
            # all attack actions should go here.

            return Attack.display_result(
                attack_function(self, character, adv, dis, attack_bonus,
                                damage_bonus))

        return modified


class Spell:
    """Represents any spell.

    Data:
    name: The spell's name.
    owner: The character associated with this spell. May be unset
        until you try to cast it.
    level: The spell's level. 0 indicates a cantrip.
    effect: A string (often long) containing a full description of the
        spell's effects.
    classes: A list of the names of all classes that have this spell
        available.
    casting_time: "Action", "Bonus action", etc.
    duration: "Instantaneous", etc.
    range: The spell's range as a string.
    components: The components that go into the spell.
    isConcentration: If the spell takes concentration or not.
    isRitual: If the spell can be cast as a ritual.

    Methods:
    cast: Handles the casting of the spell, including whether you can
        cast it with the spell slots you have remaining.
    """

    def __init__(self, jf):
        self.name = jf.get('/name')
        self.level = jf.get('/level')
        self.effect = jf.get('/effect')
        self.classes = jf.get('/class')
        self.casting_time = jf.get('/casting_time')
        self.duration = jf.get('/duration')
        self.range = jf.get('/range')
        self.components = jf.get('/components')
        self.school = jf.get('/school')
        self.isRitual = jf.get('/ritual')
        self.isConcentration = jf.get('/concentration')
        self.owner = None

    def __str__(self):
        return self.name

    def cast(self):
        # Returns a string of the effect of the spell
        if self.level > 0:
            try:
                self.owner.spell_spend(self)
            except OutOfSpells as e:
                # return str(e)
                raise e
        return self.effect

    def ritual_cast(self):
        if self.isRitual:
            return self.effect
        return ''

    def is_available(self, character):
        return True
        # for (c, obj, lv) in character.classes:
        #     if c in self.classes:
        #         return True
        # return False

    def set_owner(self, character):
        if isinstance(character, Character):
            self.owner = character
        else:
            raise ValueError("You must give a Character.")


class SpellsPrepared:
    """Handles what spells you have prepared at any given time.

    Data:
    spells: A dict of spell name: Spell object
    prepared: A set of all spell names you have prepared.
    prepared_today: A set of spell names that you prepared for today.
    always_prepared: A set of spell names that you always have prepared (domain
        spells and the like.)


    Methods:
    prepare: Prepare a spell given its name. Can prepare permanently (adding to
        always_prepared) if perma=True.
    unprepare: Unprepares a spell given its name.
    """

    def __init__(self, jf, character):
        self.record = jf
        self.char = character
        self.spells = {}
        for name in self.prepared:
            self.spells[name] = self.load_from_file(name)

    def __iter__(self):
        return (obj for obj in self.spells.values())

    def __getitem__(self, key):
        return self.spells[key]

    @property
    def prepared(self):
        today = set(self.record.get('/spells_prepared/prepared_today'))
        always = set(self.record.get('/spells_prepared/always_prepared'))
        bonuses = set(self.char.bonuses.get('always_prepared', []))
        return today | always | bonuses

    @property
    def prepared_today(self):
        return set(self.record.get('/spells_prepared/prepared_today'))

    @prepared_today.setter
    def prepared_today(self, value):
        # value is expected to be a set
        self.record.set('/spells_prepared/prepared_today', list(value))

    @property
    def always_prepared(self):
        return set(self.record.get('/spells_prepared/always_prepared'))

    @always_prepared.setter
    def always_prepared(self, value):
        self.record.set('/spells_prepared/always_prepared', list(value))

    def objects(self):
        return self.spells.values()

    def load_from_file(self, name):
        d = 'spell/'
        n = h.clean(name) + '.spell'
        jf = iface.JSONInterface(d + n)
        if jf.get('/damage'):
            tp = SpellAttack
        else:
            tp = Spell
        obj = tp(jf)
        obj.set_owner(self.char)
        return obj

    def unprepare(self, name):
        # if (name in self.prepared):
        #     path = '/spells_prepared/{}'.format(name)
        #     if (not self.record.get(path + '/always_prepared')):
        #         self.record.delete(path)
        if name in self.prepared_today:
            self.prepared_today -= {name}
            del self.spells[name]
            return True
        else:
            return False

    def prepare(self, name, perma=False):
        if name in self.prepared:
            return False
        obj = self.load_from_file(name)
        if obj.is_available(self.char):
            if perma:
                self.always_prepared |= {name}
            else:
                self.prepared_today |= {name}
            self.spells[name] = obj
            return True
        else:
            return False


class SpellAttack(Spell, Attack):
    """Represents a spell that does damage.

    These lists are "As Spell, plus..."

    Data:
    attack_roll: If True, make an attack roll when attacking with this
        spell. Otherwise targets make a saving throw.
    attack_save: The name of the ability that the target makes a save
        with.

    Methods:
    attack: Make an attack with this spell.
    """

    def __init__(self, jf):
        Spell.__init__(self, jf)
        Attack.__init__(self, jf)
        self.attack_roll = jf.get('/attack_roll')
        if not self.attack_roll:
            self.save = jf.get('/save')

    def set_owner(self, character):
        Spell.set_owner(self, character)
        if self.level == 0:
            # Apply cantrip damage scaling
            rep = lambda m: str(int(m.group(0)) * self.owner.cantrip_scale)
            self.damage_dice = re.sub(r'\d+', rep, self.damage_dice, count=1)

    @Attack.attackwrap
    def attack(self, character, adv, dis, attack_bonus, damage_bonus):
        try:
            self.cast()
        except OutOfSpells as error:
            return '', '', str(error)
        attacks = []
        damages = []
        if self.level == 0:
            s = character.bonuses.get('cantrip_damage', 0)
            extraDamage = character.parse_vars(s)
        else:
            extradamage = 0
        if (self.attack_roll):
            dice = h.d20_roll(adv, dis, character.bonuses.get('lucky', False))
            for each in range(self.num_targets):
                # using += because it's hella faster
                attack = r.compile(dice)
                attack += r.compile(attack_bonus)
                attack += r.compile(character.proficiency)
                attack += r.compile(character.relevant_abil(self))
                final = attack.evaluate()
                if (attack.is_fail()):
                    # Crit fail
                    attack_roll = 'Crit fail.'
                    damage_roll = r.compile(0)
                elif (attack.is_critical()):
                    # Critical hit
                    attack_roll = 'Critical hit!'
                    damage = r.compile(self.damage_dice)
                    damage += r.compile(damage_bonus)
                    damage += r.compile(extradamage)
                    damage.critify()
                    damage_roll = damage.evaluate()
                else:
                    # Normal attack
                    attack_roll = attack.evaluate()
                    damage = r.compile(self.damage_dice)
                    damage += r.compile(damage_bonus)
                    damage += r.compile(extradamage)
                    damage_roll = damage.evaluate()
                attacks.append(attack_roll)
                damages.append(damage_roll)
        else:
            formatstr = 'Targets make a DC {n} {t} save.'
            attacks.append(formatstr.format(n=character.save_DC(self),
                                            t=self.save))
            damage_mods = r.basic(damage_bonus) + extradamage
            damage = r.basic(self.damage_dice) + damage_mods
            damages.append(damage)
        return attacks, damages, self.effect


class Item:
    """Represents any item that you could own.

    Data:
    name: The item's name.
    weight: How much one of the item weighs.
    value: How much one of the item is worth, in gp.
    consumes: If this item consumes some item when used, it returns that.
    effect: A description of the effects of the item when used.
    description: A description of the item.

    Methods:
    use: Consume an item if applicable and return the effect.
    get: Get a value from the object's file.
    describe: Return the description of the item.
    """

    def __init__(self, jf):
        """jf is a JSONInterface to the item's file, owner is a Character"""
        self.record = jf
        self.name = jf.get('/name')
        self.value = jf.get('/value')
        self.weight = jf.get('/weight')
        self.consumes = jf.get('/consumes')
        self.effect = jf.get('/effect')
        self.description = jf.get('/description')
        self.owner = None

    def __str__(self):
        return self.name

    def __getattr__(self, key):
        return self.record.get('/' + key)

    def get(self, key):
        return self.__getattr__(key)

    def set_owner(self, character):
        if isinstance(character, Character):
            self.owner = character
        else:
            raise ValueError("You must give a Character.")

    def use(self):
        if self.owner:
            self.owner.item_consume(self.consumes)
        return self.effect

    def describe(self):
        return self.description


class Weapon(Attack, Item):
    """Represents a weapon.

    Data:
    Only inherited

    Methods:
    attack: Make an attack with this weapon.
    """

    def __init__(self, jf):
        Attack.__init__(self, jf)
        Item.__init__(self, jf)
        self.hands = jf.get('/hands')
        self.classification = jf.get('/type')
        self.ability = jf.get('/ability')
        self.magic_bonus = {}

    @Attack.attackwrap
    def attack(self, character, adv, dis, attack_bonus, damage_bonus):
        dice = h.d20_roll(adv, dis, character.bonuses.get('lucky', False))

        attacks = []
        damages = []
        abil = h.modifier(character.relevant_abil(self))
        for all in range(self.num_targets
                         + character.bonuses.get('attacks', 0)):
            # attack_roll = r.roll(dice, option=o)
            # attack_mods = (r.roll(attack_bonus, option=o)
            #                + r.roll(character.proficiency, option=o)
            #                + abil
            #                + r.roll(self.magic_bonus.get('attack', 0), option=o))
            attack = r.compile(dice)
            attack += r.compile(attack_bonus)
            attack += r.compile(character.proficiency)
            attack += r.compile(abil)
            attack += r.compile(self.magic_bonus.get('attack', 0))
            attack_roll = attack.evaluate()

            if (attack.is_fail()):
                # Crit fail
                attack_roll = 'Crit fail.'
                damage_roll = 0
            elif (attack.is_critical()):
                # Critical hit
                attack_roll = 'Critical hit!'
                damage = r.compile(self.damage_dice)
                damage += r.compile(self.magic_bonus.get('attack', 0))
                damage += r.compile(damage_bonus)
                damage.critify()
                damage_roll = damage.evaluate()
            else:
                # Normal attack
                damage = r.compile(self.damage_dice)
                damage += r.compile(self.magic_bonus.get('attack', 0))
                damage += r.compile(damage_bonus)
                damage_roll = damage.evaluate()
            attacks.append(attack_roll)
            damages.append(damage_roll)
        return (attacks, damages, self.effect)


class RangedWeapon(Weapon):
    """Represents a ranged weapon.

    These lists are "As Weapon, plus..."

    Data:
    range: A string with the range of the weapon.

    Methods:
    spendAmmo: Expends a piece of ammunition by telling the character
        to decrement their ammunition count.
    """

    def __init__(self, jf):
        Weapon.__init__(self, jf)
        self.range = jf.get('/range')

    def spend_ammo(self):
        try:
            self.owner.item_consume(self.consumes)
        except OutOfItems:
            raise
            # NOTE: This exception needs to be caught at the attack level

    def attack(self, character, adv, dis, attack_bonus, damage_bonus):
        try:
            self.spend_ammo()
        except OutOfItems as caught:
            return '', '', str(caught)
        return Weapon.attack(self, character, adv, dis, attack_bonus,
                             damage_bonus)


# noinspection PyPep8Naming
class Armor(Item):
    """Represents a set of armor.

    Data:
    base_AC: Your base AC when wearing this armor.
    bonus_AC: Any AC bonus conferred by this armor (most commonly a shield).
    type: Light, Medium, Heavy, or Shield.

    Methods:
    get_AC: Given the character's dex mod, return what base AC this armor gives
        them.
    """

    def __init__(self, jf):
        Item.__init__(self, jf)
        self.base_AC = self.record.get('/base_AC') or 10
        self.bonus_AC = self.record.get('/bonus/AC') or 0
        self.type = self.record.get('/type')

    def get_AC(self, dexmod):
        if self.type == 'LightArmor' or self.type == 'Clothes':
            effective = dexmod
        elif self.type == 'MediumArmor':
            effective = dexmod if (dexmod <= 2) else 2
        elif self.type == 'HeavyArmor':
            effective = 0
        else:
            return 0
        return self.base_AC + effective


class MagicItem(Item):
    """Represents an arbitrary magic item.

    Data:
    magic_bonus: A dict mapping applicability (such as damage or AC)
        to rollable strings. For instance, a magic weapon could have a
        +1 to attack rolls and +1d4 to damage, which would be shown as
        {"attack": 1, "damage": ["1d4", "Fire"]}
    effects: A (often long) string describing the effects of using
        this item.

    Methods:
    activate: Builds on Item.use() and returns a description of the
        effects of the magic item.
    """

    def __init__(self, jf):
        Item.__init__(self, jf)
        self.magic_bonus = jf.get('/bonus')

    def set_owner(self, character):
        pass


class MagicCharge(Resource):
    """Magic item charge is a special kind of resource.

    Data:
    regains: How many charges are regained when it recharges.

    Methods:
    rest: Roll self.regain and get back that many charges.
    """

    def __init__(self, jf, path, defjf=None, defpath=None):
        Resource.__init__(self, jf, path, defjf, defpath)
        self.regains = self.definition.get(self.defpath + '/regains')

    def rest(self, what):
        # Overrides the base method because that assumes it will fully
        #   recharge on a long rest, which is usually reasonable but not here
        if what == 'long':
            if self.recharge in ['long rest', 'short rest', 'turn']:
                self.regain(r.basic(self.regains))
                return self.number
        if what == 'short':
            if self.recharge == 'short rest' or self.recharge == 'turn':
                self.regain(r.basic(self.regains))
                return self.number
        if what == 'turn':
            if self.recharge == 'turn':
                self.regain(r.basic(self.regains))
                return self.number


class MagicArmor(MagicItem, Armor):
    def __init__(self, jf):
        MagicItem.__init__(self, jf)
        Armor.__init__(self, jf)


class MagicWeapon(MagicItem, Weapon):
    def __init__(self, jf):
        MagicItem.__init__(self, jf)
        Weapon.__init__(self, jf)


class MagicRangedWeapon(MagicItem, RangedWeapon):
    def __init__(self, jf):
        MagicItem.__init__(self, jf)
        RangedWeapon.__init__(self, jf)
