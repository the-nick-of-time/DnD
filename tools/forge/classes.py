import re
from collections import OrderedDict
from functools import wraps

import tools.libraries.rolling as r
import tools.forge.helpers as h
# import gui

__all__ = ['Character', 'Weapon', 'Spell', 'SpellAttack', 'Class',
           'RangedWeapon', 'Armor', 'Item', 'MagicItem']


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

    def __init__(self, jf):
        self.name = jf.get('/name')
        self.hit_dice = jf.get('/hit_dice')
        self.saves = jf.get('/saves')
        self.features = jf.get('/features')

    def superclass_hook(self):
        """Adds features from all superclasses of this one."""
        pass

    def get_features(self, level):
        """Gets the current features given a certain class level."""
        for name in self.features:
            for lv in self.features[name]:
                if (int(lv) <= level):
                    # Add it to the set of enabled features
                    pass

    def use_resource(self, name, howmany):
        pass


class Resource:
    def __init__(self, jf):
        self.iface = jf
        self.name = jf.get('/name')
        self.number = jf.get('/number')
        self.value = jf.get('/value')
        self.recharge = jf.get('/recharge')

    def use(self, howmany):
        if (self.number < howmany):
            return 0
        if (isinstance(self.value, str)):
            return r.roll('+'.join([self.join] * howmany))
        return howmany * self.value

    def regain(self, howmany):
        ...

    def reset(self):
        ...

    def rest(self, what):
        if (what == 'long'):
            self.reset()
            return self.number
        if (what == 'short'):
            if (self.recharge == 'short rest'):
                self.reset()
                return self.number
        return -1


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
        self.abilities = jf.get('/abilities')
        self.skills = jf.get('/skills')
        self.saves = jf.get('/saves')
        self.spell_slots = jf.get('/spell_slots')
        self.bonuses = self.get_bonuses()
        self.death_save_fails = 0
        self.conditions = set()

    def __str__(self):
        return self.name

    def __getattribute__(self, key):
        for name in self.conditions:
            print(h.condition_defs[name])
        return self.__getattr__(key)

    def add_condition(self, name):
        if (name == 'exhaustion'):
            for i in range(6):
                fmt = 'exhaustion{}'
                if (fmt.format(i + 1) in self.conditions):
                    self.conditions.remove(fmt.format(i + 1))
                    self.conditions.add(fmt.format(i + 2))
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

    def spell_spend(self, spell):
        if (self.spell_slots[spell.level] > 0):
            self.spell_slots[spell.level] -= 1
        else:
            raise (OutOfSpells(self, spell))

    def item_consume(self, name):
        count = self.inventory.getq(name)
        if (count > 0):
            self.inventory.setq(name, count - 1)
        else:
            raise OutOfItems(self, name)

    def ability_check(self, which, skill=''):
        applyskill = skill in self.skills
        ability = h.modifier(self.abilities[which])
        return (r.roll('1d20') + ability
                + self.proficiency if applyskill else 0
                + self.bonuses['check'][which] + self.bonuses['skill'][skill])

    def ability_save(self, which):
        applyprof = which in self.saves
        return (r.roll('1d20') + h.modifier(self.abilities[which])
                + self.proficiency if applyprof else 0 + self.bonuses)

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
        bonuses = {}
        for item in inventory:
            newbonus = item.get('/bonus')
            if (newbonus is not None):
                for var, amount in newbonus.items():
                    if (var not in bonuses):
                        bonuses.update((var, amount))
                    else:
                        bonuses[var] += amount
        return bonuses

    def set_abilities(self, name, value):
        self.abilities[name] = value
        self.record.set('/abilities/' + name, self.abilities[name])

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
        for c, lv in self.classes:
            if (c.caster_type == 'full' or c.caster_type == 'warlock'):
                _level += lv
            elif (c.caster_type == 'half'):
                _level += int(lv / 2)
        return _level

    @property
    def proficiency(self):
        c, lv = self.classes[0]
        return c.get('/proficiency')[self.proficiencyDice][self.level - 1]

    def save_DC(self, spell):
        return (8
                + self.bonuses.get('save_DC', 0)
                + h.modifier(self.relevant_abil(spell)))

    def relevant_abil(self, forwhat):
        if (isinstance(forwhat, Spell)):
            sharedclasses = set(forwhat.classes) & set(self.classes.names())
            if (sharedclasses):
                candidate = 0
                for name in sharedclasses:
                    abilname = self.classes[name].get('/spell/ability')
                    score = self.abilities[abilname]
                    if score > candidate:
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
            raise ValueError('This must be called with a spell or a weapon.')


class Inventory:
    """Handles an inventory. Does not depend on a Character."""

    def __init__(self, jf):
        """
        Parameters
        ----------
        jf: a JSONInterface to the character file
        """
        self.record = jf
        self.data = jf.get('/inventory')
        self.cache = {}

    def __getitem__(self, name):
        try:
            return self.cache[name]
        except KeyError as e:
            cache[name] = self.hook(name)

    def __iter__(self):
        return (name for name in self.data)

    def setq(self, name, value):
        """Sets the quantity of an object."""
        self.data[name]['quantity'] = value
        self.export(name=name)

    def getq(self, name):
        """Gets the number of an object you have.
        Returns
        -------
        number if named item exists, else 0
        """
        try:
            return self.data[name]['quantity']
        except KeyError:
            return 0

    def newslot(self, name, quantity=1, type='.item', equipped=False):
        """Creates a new item in the inventory."""
        self.data[name] = OrderedDict((('quantity', quantity), ('type', type),
                                       ('equipped', equipped)))
        try:
            if (type.startswith('.')):
                filename = h.clean(name) + type
            else:
                filename = type
            self.hook()
        except FileNotFoundError:
            # TODO: notify you that it failed
            pass
        self.export(name=name)

    def export(self, name=None):
        """
        Parameters
        ----------
        [name]: If None (the default), updates all entries in the JSONInterface
            with their current values. Otherwise only update the named field.

        Returns
        -------
        True if the operation was successful else False.
        """
        from tools.forge.helpers import clean
        if (name is None):
            self.record.set('/inventory', self.data)
            return True
        else:
            try:
                self.record.set('/inventory/' + name, self.data[name])
                return True
            except KeyError:
                # FIXME: This may fail too silently
                return False

    def hook(self, name):
        """Find the item's file and load it into an Item.
        Parameters
        ----------
        name: The name of the item to be hooked

        Returns
        -------
        An object of a type depending on the item's extension.
        """
        directory = '{direc}/{name}'
        item = self.data[name]
        location = item['type'].split(sep='.')
        if (location[0] == ''):
            # Leading . indicates name of object is included in path
            location[0] = h.clean(name)
            deeper = False
        else:
            deeper = True
        filename = directory.format(
            direc=location[-1], name='.'.join(location))
        try:
            iface = JSONInterface(filename, PREFIX=name if deeper else '')
        except FileNotFoundError:
            print(filename, ' not found')
            iface = None
        return type_select(item['type'])(iface)


class HPhandler:
    def __init__(self, jf):
        self.record = jf

    def change_HP(self, amount):
        """Changes HP by any valid roll as the amount."""
        delta = r.roll(amount)
        if (delta == 0):
            return 0
        current = self.record.get('/HP/current')
        if (delta < 0):
            temp = self.record.get('/HP/temp')
            if (abs(delta) > temp):
                delta += temp
                temp = 0
                current += delta
                self.record.set('/HP/temp', temp)
                self.record.set('/HP/current', current)
                return delta
            else:
                temp += delta
                self.record.set('/HP/temp', temp)
                return 0
        else:
            max_ = self.record.get('/HP/max')
            delta = delta if (current + delta <= max_) else max_ - current
            current += delta
            self.record.set('/HP/current', current)
            return delta

    def temp_HP(self, amount):
        """Adds a rollable amount to your temp HP"""
        delta = r.roll(amount)
        if (delta == 0):
            return self.data
        temp = self.record.get('/HP/temp')
        if (delta > temp):
            temp = delta
        self.record.set('/HP/temp', temp)
        return self.data

    def use_HD(self, which):
        """Use a specific one of your hit dice."""
        num = self.record.get('/HP/HD/' + which)
        conmod = h.modifier(self.record.get('/abilities/Constitution'))
        if (num > 0):
            self.record.set('/HP/HD/' + which, num - 1)
            return self.change_HP(r.roll(which) + conmod)
        else:
            return None

    def long_rest(self):
        mx = self.record.get('/HP/max')
        self.record.set('/HP/current', mx)
        for c, lv in self.record.classes:
            type = c.get('/hit_dice')
            curr = self.record.get('/HP/HD/' + type)
            recover = int(lv / 2) + 1
            self.record.set('/HP/HD/' + type,
                            curr + recover if curr + recover < lv else lv)


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
        self.classes = jf.get('/classes')
        self.casting_time = jf.get('/casting_time')
        self.duration = jf.get('/duration')
        self.range = jf.get('/range')
        self.components = jf.get('/components')
        self.owner = None

    def __str__(self):
        return self.name

    def cast(self):
        # Returns a string of the effect of the spell
        if (self.level > 0):
            try:
                self.owner.spell_spend(self.level)
            except OutOfSpells:
                raise
        return self.effects

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
        super().__init__(jf)
        if (self.level == 0):
            self.damage_dice = '+'.join([self.damage_dice] *
                                        self.owner.cantrip_scale)
        self.attack_roll = bool(jf.get('/attack_roll'))
        if (not self.attack_roll):
            self.attack_save = jf.get('/save')
        self.abil_add = jf.get('/add_abil')

    @Attack.attackwrap
    def attack(self, character, adv, dis, attack_bonus, damage_bonus):
        try:
            self.cast()
        except OutOfSpells as error:
            return ('', '', str(error))


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
        self.name = jf.get('/name')
        self.value = jf.get('/value')
        self.weight = jf.get('/weight')
        self.consumable = jf.get('/consumable')
        self.effect = jf.get('/effect')
        self.owner = None

    def __str__(self):
        return self.name

    def setowner(self, person):
        if (isinstance(character, Character)):
            self.owner = character
        else:
            raise ValueError("You must give a Character.")

    def use(self):
        if (self.consumable and self.owner):
            self.owner.item_consume(self.name)
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
        self.hands = jf.get('/hands')
        self.classification = jf.get('/type')
        self.ability = jf.get('/ability')

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
    def __init__(self):
        pass


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
    pass


class MagicArmor(MagicItem, Armor):
    pass


class MagicWeapon(MagicItem, Weapon):
    pass


class MagicRangedWeapon(MagicItem, RangedWeapon):
    pass


class MyError(Exception):
    pass


class OutOfSpells(MyError):
    def __init__(self, character, spell):
        self.character = character
        self.spell = spell

    def __str__(self):
        formatstr = '{char} has no spell slots of level {lv} remaining.'
        return formatstr.format(char=self.character.name, lv=self.spell.level)


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
