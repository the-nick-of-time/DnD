import re
import os
from collections import OrderedDict, defaultdict
# SO I'm seriously considering not using a defaultdict as such, as it inserts its default values into the dict itself
# If these are ever actually written to a file, it will be cluttered
from functools import wraps
from math import ceil

# import tools.libraries.rolling as r
# import tools.forge.helpers as h
import rolling as r
import helpers as h
import interface as iface
import ClassMap as cm

# __all__ = ['Character', 'Weapon', 'Spell', 'SpellAttack', 'Class',
#            'RangedWeapon', 'Armor', 'Item', 'MagicItem']


class Class:
    """Nonspecific representation of a D&D class.

    Contained data:
    name: the name of the class
    skills: Tuple of strings detailing the skill proficiencies
    saves: Tuple of strings detailing the save proficiencies

    caster_type: '', 'half', 'full', or 'warlock'.
    caster_abil: An ability name.

    features: a dict mapping names to level: description dicts

    resources: special class-specific resources like sorcerer points


    Contained methods:
    useresource
    """

    def __init__(self, jf, classlevel):
        self.record = jf
        self.name = jf.get('/name')
        self.level = classlevel
        # self.hit_dice = jf.get('/hit_dice')
        # self.saves = jf.get('/saves')
        self._features = jf.get('*/features')
        self.features = set()
        self.get_features()

    def get(self, key):
        return self.record.get(key)

    def get_features(self):
        """Gets the current features given a certain class level."""
        pass
        # for name in self._features:
        #     for lv in self._features[name]:
        #         if (int(lv) <= self.level):
        #             # Add it to the set of enabled features
        #             self.features.add(self._features[name][lv])


class Resource:
    def __init__(self, jf, path, defjf=None, defpath=None):
        self.record = jf
        self.definition = defjf if (defjf is not None) else jf
        self.path = path
        self.defpath = defpath if (defpath is not None) else path
        self.name = self.definition.get(self.defpath + '/name')
        self.value = self.definition.get(self.defpath + '/value')
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
        if (val is not None):
            return val
        return self.definition.get(self.defpath + '/maxnumber')

    @maxnumber.setter
    def maxnumber(self, value):
        self.record.set(self.path + '/maxnumber', value)

    def use(self, howmany):
        if (self.number < howmany):
            raise LowOnResource(self)
        if (isinstance(self.value, str)):
            self.number -= howmany
            return r.roll('+'.join([self.value] * howmany))
        return howmany * self.value

    def regain(self, howmany):
        if (self.number + howmany > self.maxnumber):
            self.reset()
        else:
            self.number += howmany

    def reset(self):
        self.number = self.maxnumber

    def rest(self, what):
        if (what == 'long'):
            self.reset()
            return self.number
        if (what == 'short'):
            if (self.recharge == 'short rest'):
                self.reset()
                return self.number
        return -1

    def write(self):
        self.record.write()


class Character:
    """Represents a PC or NPC.

    Contained data:
    name: The name of the character.
    class_levels: A ClassMap object.
    level: The total level of the character, equivalent to
        class_levels.sum()
    caster_level: The total caster level of the character.
    abilities: A dictionary mapping ability names (abbreviations) to
        scores.
    inventory: A list of equipment, tagged with whether they are
        equipped. In the form [name, count, equipped]
    AC: The current AC of the character.
    proficiency: The proficiency bonus of the character. Allowed to
        use proficiency dice.

    HP: An integer with the character's current hit points.
    HP_max: An integer with the character's maximum HP.
    HP_temp: An integer with the character's current temporary HP.

    spell_slots: A list of length <= 10 of the number of spell slots
        that are currently available.
    spell_prepared: A list of strings with the names of spells that are
        currently prepared.
    spell_save: An integer with the character's spell save DC.


    Contained methods:
    HP_change: Takes the integer value of a change to HP (may be
        produced by a roll) and alters the character's HP.
            HP_change(self, amount)

    spell_reset: Resets all spell slots to their maximum values.
    spell_spend: Takes the level of the spell and deducts it from the
        character's availability.
    spell_recover: Takes the level of the spell slot and adds it to
        the character's available spells.

    abil_get_relevant: When called by a weapon or spell, returns the
        relevant ability name. For instance, when a multiclass
        druid/sorcerer casts a spell, it may use either the character's
        Wisdom or Charisma. When there are multiple options, it returns
        the one with the best ability score.
            abil_get_relevant(self, action)
    abil_check: Performs an ability check with the specified ability.
        If skill is given, it is a skill check of that type.
            abil_check(self, abil, skill='')
    abil_save: Rolls a saving throw for the specified ability.
            abil_save(self, abil)

    AC_calc: Calculate the AC of the character.

    item_consume: Use up a consumable item.
    """
    proficiencyDice = False

    def __init__(self, jf):
        self.record = jf
        self.name = jf.get('/name')
        self.abilities = jf.get('/abilities')
        self.skills = jf.get('/skills')
        self.saves = jf.get('/saves')
        lv = jf.get('/level')
        self.classes = cm.ClassMap(lv)
        self.hp = HPhandler(self.record)
        self.inventory = Inventory(self.record)
        self.attacks = {}
        self.register_attacks()
        self.bonuses = self.get_bonuses()
        self.death_save_fails = 0
        self.conditions = set()
        self.proficiencyDice = False
        self.lucky = False  # except that halflings get it
        # self.spells = SpellsPrepared(jf, self)

    def __str__(self):
        return self.name

    def __getattr__(self, key):
        if (key.lower() == 'str_mod'):
            return h.modifier(self.abilities['strength'])
        if (key.lower() == 'dex_mod'):
            return h.modifier(self.abilities['dexterity'])
        if (key.lower() == 'con_mod'):
            return h.modifier(self.abilities['constitution'])
        if (key.lower() == 'int_mod'):
            return h.modifier(self.abilities['intelligence'])
        if (key.lower() == 'wis_mod'):
            return h.modifier(self.abilities['wisdom'])
        if (key.lower() == 'cha_mod'):
            return h.modifier(self.abilities['charisma'])
        if (key.endswith('_level')):
            head, _, _ = key.partition('_')
            try:
                cl = self.classes[head]
            except KeyError:
                return 0
            return cl.level

    def add_condition(self, name):
        if (name == 'exhaustion'):
            for i in range(6):
                fmt = 'exhaustion{}'
                if (fmt.format(i + 1) in self.conditions):
                    self.conditions.remove(fmt.format(i + 1))
                    self.conditions.add(fmt.format(i + 2))
                    return True
            self.conditions.add('exhaustion1')
            return True
        else:
            self.conditions.add(name)
            return True

    def remove_condition(self, name):
        if (name == 'exhaustion'):
            for i in range(6):
                fmt = 'exhaustion{}'
                if (fmt.format(i + 1) in self.conditions):
                    self.conditions.remove(fmt.format(i + 1))
                    if (i > 0):
                        self.conditions.add(fmt.format(i))
                    return True
        else:
            try:
                self.conditions.remove(name)
                return True
            except KeyError:
                return False

    def register_attacks(self):
        for item in self.inventory:
            if (isinstance(item, Attack)):
                self.attacks[item.name] = item
        # TODO: Work out spells as well; needs classification of spells as attacks

    def spell_spend(self, spell):
        if (isinstance(spell, int)):
            path = '/spell_slots/' + str(spell)
        else:
            path = '/spell_slots/' + str(spell.level)
        num = self.record.get(path)
        if (num > 0):
            self.record.set(path, num-1)
        else:
            raise (OutOfSpells(self, spell))

    def ability_check(self, which, skill='', adv=False, dis=False):
        applyskill = skill in self.skills
        ability = h.modifier(self.abilities[which])
        rollstr = '2d20h1' if (adv and not dis) else '2d20l1' if (dis and not adv) else '1d20'
        roll = r.roll(rollstr)
        if (applyskill):
            prof = self.proficiency
        else:
            prof = 0
        bon = self.bonuses['check'][which] + self.bonuses['skill'][skill]
        return (roll + prof + ability + bon, prof + ability + bon, roll)

    def ability_save(self, which, adv=False, dis=False):
        applyprof = which in self.saves
        if (applyprof):
            prof = self.proficiency
        else:
            prof = 0
        ability = h.modifier(self.abilities[which])
        rollstr = '2d20h1' if (adv and not dis) else '2d20l1' if (dis and not adv) else '1d20'
        roll = r.roll(rollstr)
        bon = self.bonuses['save'][which]
        return (roll + prof + ability + bon, prof + ability + bon, roll)

    def death_save(self):
        val = r.roll('1d20')
        if (val == 1):
            self.death_save_fails += 2
        elif (val == 20):
            self.death_save_fails = 0
            self.remove_condition('dying')
            # Signal that you're better now
        elif (val < 10):
            self.death_save_fails += 1
        if (self.death_save_fails >= 3):
            self.conditions.add('dead')

    def get_bonuses(self):
        bonuses = defaultdict(lambda: 0)
        for item in self.inventory:
            newbonus = item.get('/bonus')
            if (newbonus is not None):
                for var, amount in newbonus.items():
                    if (var not in bonuses):
                        bonuses.update({var: amount})
                    else:
                        bonuses[var] += amount
        return bonuses

    def set_abilities(self, name, value):
        self.abilities[name] = value
        self.record.set('/abilities/' + name, self.abilities[name])

    @property
    def cantrip_scale(self):
        for n, cl, lv in self.classes:
            caster_type = cl.get('/spellcasting/levels')
            if (caster_type is None):
                continue
            else:
                # path = '/cantrip_damage/{}'.format(self.caster_level - 1)
                path = '/cantrip_damage/{}'.format(self.level - 1)  # Which is it?
                return cl.get(path)
        return 1

    @property
    def weaponprof(self):
        total = []
        for c, lv in self.classes:
            total.extend(c.weapons['types'])
            total.extend(c.weapons['specific'])
        return total

    @property
    def AC(self):
        baseAC = 0
        bonusAC = self.bonuses['AC']
        for item in self.inventory:
            if (item.get('/equipped')):
                ac = item.get('/AC')
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
            if (caster_type is None):
                continue
            elif (caster_type == 'full' or caster_type == 'warlock'):
                _level += lv
                continue
            elif (caster_type == 'half'):
                _level += int(lv / 2)
                continue
            elif (caster_type == 'third'):
                _level += int(lv / 3)
                continue
        return _level

    @property
    def spell_slots(self):
        return self.record.get('/spell_slots')

    def spell_slots_get(self, level):
        block = self.record.get('/spell_slots')
        if (level == '*'):
            return block
        return block[level]

    def spell_slots_set(self, level, value):
        if (level == '*'):
            self.record.set('/spell_slots', value)
        elif (isinstance(level, int)):
            self.record.set('/spell_slots/' + str(level), value)

    @property
    def max_spell_slots(self):
        # This will fuck up on warlock multiclasses, I think I need to treat those spell slots as a Resource instead
        cl = self.classes[0]
        if (len(self.classes) == 1):
            t = cl.get('/spellcasting/slots')
        else:
            t = 'full'
        path = '/slots/{}/{}'.format(t, self.caster_level)
        return cl.get(path)

    @property
    def proficiency(self):
        c = self.classes[0]
        return c.get('/proficiency')[int(self.proficiencyDice)][self.level - 1]

    def save_DC(self, spell):
        return (8
                + self.bonuses['save_DC']
                + h.modifier(self.relevant_abil(spell)))

    def relevant_abil(self, forwhat):
        if (isinstance(forwhat, Spell)):
            sharedclasses = set(forwhat.classes) & set(self.classes.names())
            if (sharedclasses):
                candidate = 0
                for name in sharedclasses:
                    abilname = self.classes[name].get('/spellcasting/ability')
                    score = self.abilities[abilname]
                    if (score > candidate):
                        candidate = score
                return candidate
            else:
                raise AttributeError('You don\'t have that spell available.')
        elif (isinstance(forwhat, Weapon)):
            candidate = 0
            for abilname in forwhat.ability:
                score = self.abilities[abilname]
                if (score > candidate):
                    candidate = score
            return candidate
        else:
            raise TypeError('This must be called with a spell or a weapon.')

    def rest(self, what):
        self.hp.rest(what)
        if (what == 'long'):
            self.record.set('/spell_slots', self.max_spell_slots[:])
        elif (what == 'short'):
            pass

    def write(self):
        self.record.set('/abilities', self.abilities)
        # self.record.set('/spell_slots', self.spell_slots)
        self.record.write()


class Inventory:
    """Handles an inventory. Does not depend on a Character."""

    def __init__(self, jf):
        """
        Parameters
        ----------
        jf: a JSONInterface to the character file
        data: the equipment portion of said file
        items: a dict of name: ItemEntry
        """
        self.record = jf
        self.items = {}
        self.load_items()

    def __getitem__(self, name):
        return self.items[name]

    def __iter__(self):
        return (entry for entry in self.items.values())

    def load_items(self):
        for name in self.record.get('/equipment'):
            path = '/equipment/' + name
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
        path = '/equipment/' + name
        self.record.set(path, OrderedDict())
        self.record.set(path + '/type', type)
        self.record.set(path + '/quantity', quantity)
        self.record.set(path + '/equipped', equipped)
        self.load_items()

    def write(self):
        self.record.write()


class ItemEntry:
    def __init__(self, jf, path, character=None):
        self.record = jf
        self.path = path
        self.person = character
        self.load_from_file()

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
        if (self.obj is not None):
            return self.obj.name
        else:
            return self.path.split(sep='/')[-1]

    @property
    def number(self):
        return self.record.get(self.path + '/quantity')

    @number.setter
    def number(self, value):
        if (not isinstance(value, int)):
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
        if (isinstance(value, bool)):
            self.record.set(self.path + '/equipped', value)
        else:
            raise TypeError('The equipped value must be bool')

    @property
    def type(self):
        return self.record.get(self.path + '/type')

    @property
    def weight(self):
        if (self.obj is not None):
            return self.obj.weight
        else:
            return 0

    @property
    def value(self):
        if (self.obj is not None):
            return self.obj.value
        else:
            return 0

    @property
    def consumable(self):
        if (self.obj is not None):
            return self.obj.consumable
        else:
            return False

    def get(self, key):
        if (self.obj is not None):
            return self.obj.get(key)
        return None

    def use(self):
        if (self.consumable):
            self.number -= 1
        if (self.obj is not None):
            return self.obj.use()
        else:
            return ''

    def describe(self):
        if (self.obj is not None):
            return self.obj.describe()
        else:
            return ''


class HPhandler:
    def __init__(self, jf):
        self.record = jf
        self.hd = {size: HDHandler(jf, size) for size in jf.get('/HP/HD')}

    @property
    def current(self):
        return self.record.get('/HP/current')

    @current.setter
    def current(self, value):
        return self.record.set('/HP/current', value)

    @property
    def max(self):
        return self.record.get('/HP/max')

    @max.setter
    def max(self, value):
        return self.record.set('/HP/max', value)

    @property
    def temp(self):
        return self.record.get('/HP/temp')

    @temp.setter
    def temp(self, value):
        return self.record.set('/HP/temp', value)

    def change_HP(self, amount):
        """Changes HP by any valid roll as the amount."""
        delta = r.roll(amount)
        if (delta == 0):
            return 0
        # current = self.record.get('/HP/current')
        current = self.current
        if (delta < 0):
            # temp = self.record.get('/HP/temp')
            temp = self.temp
            if (abs(delta) > temp):
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
        delta = r.roll(amount)
        if (delta == 0):
            return 0
        temp = self.record.get('/HP/temp')
        if (delta > temp):
            temp = delta
        self.record.set('/HP/temp', temp)
        return 0

    def use_HD(self, which):
        """Use a specific one of your hit dice."""
        return self.change_HP(self.hd[which].use_HD())

    def rest(self, what):
        if (what == 'long'):
            # mx = self.record.get('/HP/max')
            # self.record.set('/HP/current', mx)
            self.current = self.max
            for obj in self.hd.values():
                obj.rest('long')

    def write(self):
        for item in self.hd.values():
            item.write()
        self.record.write()


class HDHandler(Resource):
    def __init__(self, jf, size):
        Resource.__init__(self, jf, '/HP/HD/' + size)
        self.name = 'Hit Die'
        self.value = size
        self.recharge = 'long'

    def use_HD(self):
        try:
            roll = self.use(1)
        except LowOnResource as e:
            return 0

        conmod = h.modifier(self.record.get('/abilities/constitution'))
        return roll+conmod if (roll+conmod > 1) else 1

    def rest(self, what):
        if (what == 'long'):
            self.regain(ceil(self.maxnumber / 2))


class Damage:
    def __init__(self, data):
        self.data = data

    def get1h(self):
        return self.data['one hand']

    def get2h(self):
        return self.data['two hands']

    def getlevel(self):
        pass


class Attack:
    """Base for other attacks.

    Contained data:
    damage_dice
    num_targets: How many targets can be hit by this attack. If the
        attack is AOE, just use a reasonable upper bound.
    path: a gui.Interface path to the attack section.

    Contained methods:
    @staticmethod
    display_result: Display the result of an attack.

    attackwrap: This decorator ensures that the attack methods of all
        subclasses are handled correctly.
    """

    def __init__(self, jf):
        self.damage_dice = jf.get('/damage')
        self.num_targets = jf.get('/attacks')

    @staticmethod
    def display_result(result):
        # IMPLEMENTATION: result must be a 3-item iterable made of:
        # an iterable of attack rolls
        # an iterable of damage rolls
        # a string of the effects of the attack
        attack_string = 'Attack rolls: ' + ', '.join(result[0])
        damage_string = 'Damage rolls: ' + ', '.join(result[1])
        effects = result[2]
        panel = gui.AttackResult(path['display'], attack_string, damage_string,
                                 effects)

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

    Contained data:
    name
    owner: The character associated with this spell. May be unset
        until you try to cast it.
    level: The spell's level. 0 indicates a cantrip.
    effects: A string (often long) containing a full description of the
        spell's effects.
    classes: A tuple with the names of all classes that have this spell
        available.

    Contained methods:
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
        self.isritual = jf.get('/ritual')
        self.isconcentration = jf.get('/concentration')
        self.owner = None

    def __str__(self):
        return self.name

    def cast(self):
        # Returns a string of the effect of the spell
        if (self.level > 0):
            try:
                self.owner.spell_spend(self)
            except OutOfSpells as e:
                return str(e)
        return self.effect

    def is_available(self, character):
        for c in character.classes:
            if c in self.classes:
                return True
        return False

    def setowner(self, character):
        if (isinstance(character, Character)):
            self.owner = character
        else:
            raise ValueError("You must give a Character.")


class SpellsPrepared:
    def __init__(self, jf, character):
        self.record = jf
        self.char = character
        self.spells = {}
        for name in self.prepared:
            self.spells[name] = self.load_from_file(name)

    @property
    def prepared(self):
        today = set(self.record.get('/spells_prepared/prepared_today'))
        always = set(self.record.get('/spells_prepared/always_prepared'))
        return today | always

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

    def objects(self):
        return self.spells.values()

    def load_from_file(self, name):
        d = 'spell/'
        n = h.clean(name) + '.spell'
        jf = iface.JSONInterface(d + n)
        if (jf.get('/damage')):
            tp = SpellAttack
        else:
            tp = Spell
        obj = tp(jf)
        obj.setowner(self.char)
        return obj

    def unprepare(self, name):
        # if (name in self.prepared):
        #     path = '/spells_prepared/{}'.format(name)
        #     if (not self.record.get(path + '/always_prepared')):
        #         self.record.delete(path)
        self.prepared_today -= {name}

    def prepare(self, name):
        obj = self.load_from_file(name)
        if (obj.is_available(self.char)):
            # self.record.set('/spells_prepared/' + name, {"always_prepared": False})
            self.prepared_today |= {name}
            self.spells[name] = obj
            return True
        else:
            return False


class SpellAttack(Spell, Attack):
    """Represents a spell that does damage.

    These lists are "As Spell, plus..."

    Contained data:
    attack_roll: If True, make an attack roll when attacking with this
        spell. Otherwise targets make a saving throw.
    attack_save: The name of the ability that the target makes a save
        with.
    abil_add: Do you add your spellcasting ability modifier to the
        damage of this spell?

    Contained methods:
    """

    def __init__(self, jf):
        Spell.__init__(self, jf)
        Attack.__init__(self, jf)
        self.attack_roll = jf.get('/attack_roll')
        if (not self.attack_roll):
            self.save = jf.get('/save')
        self.add_abil = jf.get('/add_abil')

    def setowner(self, character):
        Spell.setowner(self, character)
        if (self.level == 0):
            self.damage_dice = '+'.join([self.damage_dice] *
                                        self.owner.cantrip_scale)

    @Attack.attackwrap
    def attack(self, character, adv, dis, attack_bonus, damage_bonus):
        try:
            self.cast()
        except OutOfSpells as error:
            return ('', '', str(error))
        attacks = []
        damages = []
        if (self.add_abil):
            abil = h.modifier(character.relevant_abil(self))
        else:
            abil = 0
        if (self.attack_roll):
            if (adv and not dis):
                dice = h.ADV if not character.lucky else h.ADV_LUCK
            elif (dis and not adv):
                dice = h.DIS if not character.lucky else h.DIS_LUCK
            else:
                dice = h.D20 if not character.lucky else h.D20_LUCK
            for each in range(self.num_targets):
                attack_roll = r.roll(dice)
                attack_mods = r.roll(attack_bonus) \
                              + r.roll(character.proficiency) \
                              + h.modifier(character.relevant_abil(self))
                if (attack_roll == 1):
                    # Crit fail
                    attack_roll = 'Crit fail.'
                    damage_roll = 0
                elif (attack_roll == 20):
                    # Critical hit
                    attack_roll = 'Critical hit!'
                    damage_mods = r.roll(damage_bonus, mode='critical') \
                                  + abil
                    damage_roll = r.roll(self.damage_dice, mode='critical') \
                                  + damage_mods
                else:
                    # Normal attack
                    attack_roll += attack_mods
                    damage_mods = r.roll(damage_bonus) + abil
                    damage_roll = r.roll(self.damage_dice) + damage_mods
                attack.append(attack_roll)
                damage.append(damage_roll)
        else:
            formatstr = 'Targets make a DC {n} {t} save.'
            attacks.append(formatstr.format(character.save_DC, self.save))
            damage_mods = r.roll(damage_bonus) + abil
            damage = r.roll(self.damage_dice) + damage_mods
            damages.append(damage)


class Item:
    """Represents any item that you could own.

    Contained data:
    name
    consumable: True if the item is consumed by being used.

    Contained methods:
    use: Decrement count if consumable and return the effect.
    """

    def __init__(self, jf):
        """jf is a JSONInterface to the item's file, owner is a Character"""
        self.record = jf
        self.name = jf.get('/name')
        self.value = jf.get('/value')
        self.weight = jf.get('/weight')
        self.consumable = jf.get('/consumable')
        self.effect = jf.get('/effect')
        self.description = jf.get('/description')
        self.owner = None

    def __str__(self):
        return self.name

    def __getattr__(self, key):
        return self.record.get(key)

    def get(self, key):
        return self.__getattr__(key)

    def setowner(self, character):
        if (isinstance(character, Character)):
            self.owner = character
        else:
            raise ValueError("You must give a Character.")

    def use(self):
        return self.effect

    def describe(self):
        return self.description


class Weapon(Attack, Item):
    """Represents a weapon.

    Contained data:
    owner: The character who is using this weapon.

    Contained methods:
    """

    def __init__(self, jf):
        Attack.__init__(self, jf)
        Item.__init__(self, jf)
        self.hands = jf.get('/hands')
        self.classification = jf.get('/type')
        self.ability = jf.get('/ability')
        self.magic_bonus = defaultdict(lambda: 0)

    @Attack.attackwrap
    def attack(self, character, adv, dis, attack_bonus, damage_bonus):
        if (adv and not dis):
            dice = '1d20h1'
        elif (dis and not adv):
            dice = '1d20l1'
        else:
            dice = '1d20'

        attack = []
        damage = []
        for all in range(self.num_targets):
            attack_roll = r.roll(dice)
            attack_mods = r.roll(attack_bonus) \
                          + r.roll(character.proficiency) \
                          + r.roll(self.magic_bonus['attack']) \
                          + character.abil_get_relevant(self, 'modifier')

            if (attack_roll == 1):
                # Crit fail
                attack_roll = 'Crit fail.'
                damage_roll = 0
            elif (attack_roll == 20):
                # Critical hit
                attack_roll = 'Critical hit!'
                damage_mods = character.abil_get_relevant(self, 'modifier') \
                              + r.roll(damage_bonus, mode='critical') \
                              + r.roll(self.magic_bonus['damage'],
                                       mode='critical')
                damage_roll = r.roll(self.damage_dice, mode='critical') \
                              + damage_mods
            else:
                # Normal attack
                attack_roll += attack_mods
                damage_mods = character.abil_get_relevant(self, 'modifier') \
                              + r.roll(damage_bonus) \
                              + r.roll(self.magic_bonus['damage'])
                damage_roll = r.roll(self.damage_dice) + damage_mods
            attack.append(attack_roll)
            damage.append(damage_roll)


class RangedWeapon(Weapon):
    """Represents a ranged weapon.

    These lists are "As Weapon, plus..."

    Contained data:
    ammunition: Which type of ammunition it uses. May be bolt, arrow,
        bullet, or its own name (if thrown).

    Contained methods:
    spendAmmo: Expends a piece of ammunition by telling the character
        to decrement their ammunition count.
    recoverAmmo: Recovers a piece of ammunition.
    """

    def __init__(self, jf):
        Weapon.__init__(self, jf)
        self.ammunition = jf.get('/ammunition')
        self.thrown = (self.ammunition == self.name)
        self.shortrange = jf.get('/range')
        self.longrange = self.shortrange * (3 if self.thrown else 4)
        self.range = '{}/{}'.format(self.shortrange, self.longrange)

    def spend_ammo(self):
        try:
            self.owner.item_consume(self.ammunition)
        except OutOfItems:
            raise
            # NOTE: This exception needs to be caught at the attack level

    def attack(self, character, adv, dis, attack_bonus, damage_bonus):
        try:
            self.spend_ammo()
        except OutOfItems as caught:
            return ('', '', str(caught))
        return Weapon.attack(self, character, adv, dis, attack_bonus,
                             damage_bonus)


class Armor(Item):
    """Represents a set of armor.

    Contained data:
    base_AC: Your base AC when wearing this armor.
    type: Light, Medium, Heavy, or Shield.

    Contained methods:
    """
    def __init__(self, jf):
        Item.__init__(self, jf)
        self.base_AC = self.record.get('/AC') or 0
        self.bonus_AC = self.record.get('/bonus/AC') or 0


class MagicItem(Item):
    """Represents an arbitrary magic item.

    Contained data:
    magic_bonus: A dict mapping applicability (such as damage or AC)
        to rollable strings. For instance, a magic weapon could have a
        +1 to attack rolls and +1d4 to damage, which would be shown as
        {"attack": 1, "damage": ["1d4", "Fire"]}
    effects: A (often long) string describing the effects of using
        this item.

    Contained methods:
    activate: Builds on Item.use() and returns a description of the
        effects of the magic item.
    """
    def __init__(self, jf):
        Item.__init__(self, jf)

    def setowner(self, character):
        pass


class MagicCharge(Resource):
    def __init__(self, jf, path, defjf=None, defpath=None):
        Resource.__init__(self, jf, path, defjf, defpath)
        self.regains = self.definition.get(self.defpath + '/regains')

    def rest(self, what):
        # Overrides the base method because that assumes it will fully
        #   recharge on a long rest, which is usually reasonable but not here
        if (what == 'long'):
            if (self.recharge == 'long rest' or self.recharge == 'short rest'):
                self.regain(r.roll(self.regains))
                return self.number
        if (what == 'short'):
            if (self.recharge == 'short rest'):
                self.regain(r.roll(self.regains))
                return self.number


class MagicArmor(MagicItem, Armor):
    pass


class MagicWeapon(MagicItem, Weapon):
    pass


class MagicRangedWeapon(MagicItem, RangedWeapon):
    pass


class MyError(Exception):
    pass


class LowOnResource(MyError):
    def __init__(self, resource):
        self.resource = resource

    def __str__(self):
        formatstr = 'You have no {rs} remaining.'
        return formatstr.format(rs=self.resource.name)


class OutOfSpells(MyError):
    def __init__(self, character, spell):
        self.character = character
        self.spell = spell

    def __str__(self):
        formatstr = '{char} has no spell slots of level {lv} remaining.'
        return formatstr.format(char=self.character.name, lv=(self.spell if isinstance(self.spell, int) else self.spell.level))


class OutOfItems(MyError):
    def __init__(self, character, item):
        self.character = character
        self.item = item

    def __str__(self):
        formatstr = '{char} has no {item}s remaining.'
        return formatstr.format(char=self.character.name, item=self.item.name)


class OverflowSpells(MyError):
    def __init__(self, character, spell):
        self.character = character
        self.spell = spell

    def __str__(self):
        formatstr = '{char} has full spell slots of level {lv} already.'
        return formatstr.format(char=self.character.name, lv=self.spell.level)
