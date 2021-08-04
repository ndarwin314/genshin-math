import numpy as np

def fast_comb(n, k):
    n, k = n + k, k
    a = np.ones((k, n - k + 1), dtype=int)
    a[0] = np.arange(n - k + 1)
    for j in range(1, k):
        reps = (n - k + j) - a[j - 1]
        a = np.repeat(a, reps, axis=1)
        ind = np.add.accumulate(reps)
        a[j, ind[:-1]] = 1 - reps[1:]
        a[j, 0] = j
        a[j] = np.add.accumulate(a[j])
    bad = np.repeat(np.reshape(np.arange(k), (k, 1)), a.shape[1], axis=1)
    return (a - bad).T


def add_dicts(d1, d2):
    new_dict = d1.copy()
    for tag, bonus in d2.items():
        if tag in new_dict:
            new_dict[tag] += bonus
        else:
            new_dict[tag] = bonus
    return new_dict

def reaction_damage(base_damage, element, attributes, enemy):

    # TODO: idk if i want this to change state or something, doing that requires doing dumb gauge bullshit
    em = attributes.em
    if DmgTag.PYRO in element:
        if enemy[Event.ENEMY_HYDRO]:
            return base_damage * amp_react_mult(False, em, attributes.reaction_bonus.get(ReactionType.VAPE, 0))
        elif enemy[Event.ENEMY_CRYO] or enemy[Event.ENEMY_FROZEN]:
            return base_damage * amp_react_mult(True, em, attributes.reaction_bonus.get(ReactionType.MELT, 0))
        elif enemy[Event.ENEMY_ELECTRO]:
            return base_damage + \
                   tf_react_dmg(ReactionType.OL, em, attributes.reaction_bonus.get(ReactionType.OL, 0), char_lvl=90)
        else:
            return base_damage
    elif DmgTag.CRYO in element:
        if enemy[Event.ENEMY_PYRO]:
            return base_damage * amp_react_mult(False, em, attributes.reaction_bonus.get(ReactionType.MELT, 0))
        elif enemy[Event.ENEMY_ELECTRO]:
            return base_damage + \
                   tf_react_dmg(ReactionType.SC, em, attributes.reaction_bonus.get(ReactionType.SC ,0), char_lvl=90)
        else:
            return base_damage
    elif DmgTag.HYDRO in element:
        if enemy[Event.ENEMY_PYRO]:
            return base_damage * amp_react_mult(True, em, attributes.reaction_bonu.get(ReactionType.VAPE, 0))
        elif enemy[Event.ENEMY_ELECTRO]:
            return base_damage + \
                   tf_react_dmg(ReactionType.EC, em, attributes.reaction_bonus.get(ReactionType.EC, 0), char_lvl=90)
        else:
            return base_damage
    elif DmgTag.ANEMO in element:
        if enemy[Event.ENEMY_PYRO] or enemy[Event.ENEMY_HYDRO] or enemy[Event.ENEMY_CRYO] or enemy[Event.ENEMY_ELECTRO]:
            return base_damage + \
                   tf_react_dmg(ReactionType.SWIRL, em, attributes.reaction_bonus.get(ReactionType.SWIRL, 0), char_lvl=90)
        else:
            return base_damage
    else:
        return base_damage

def calc_attack(base_atk, atk_pct, flat_atk):
    return base_atk * (1 + atk_pct) + flat_atk

def calc_resist(enemy_resistance):
    if enemy_resistance < 0:
        return 1 - enemy_resistance / 2
    elif enemy_resistance < 0.75:
        return 1 - enemy_resistance
    else:
        return 1 / (4 * enemy_resistance + 1)

def outgoing_damage(attributes, atk_scaling, dmg_types, enemy):
    atk = calc_attack(attributes.base_atk, attributes.atk_pct, attributes.flat_atk)
    dmg_bonus = total_dmg_bonus(dmg_types, attributes)
    crit_damage = base_damage(atk, atk_scaling, dmg_bonus) * crit_multiplier(attributes.crit_rate, attributes.crit_dmg)
    return reaction_damage(crit_damage, dmg_types, attributes, enemy)

def base_damage(atk, atk_scaling, damage_bonus, defense=0, def_scaling=0):
    return (atk * atk_scaling + defense * def_scaling) * (1 + damage_bonus)

def crit_multiplier(crit_rate, crit_damage):
    return 1 + crit_rate * crit_damage


def amp_react_mult(is_strong, em, bonus):
    multiplier = 2 if is_strong else 1.5
    return multiplier * (1 + 2.78 * em / (1400 + em) + bonus)


# Transformative reactions
def tf_react_dmg(react_type, em, bonus, char_lvl=80, enemy_resist_pct=.1):
    mult_type_dict = {
        ReactionType.OL: 4,
        ReactionType.SHATTER: 3,
        ReactionType.EC: 2.4,
        ReactionType.SWIRL: 1.2,
        ReactionType.SC: 1,
    }
    bonus_mult = 1 + 16 * em / (2000 + em) + bonus
    lvl_mult = .0002325 * char_lvl ** 3 + .05547 * char_lvl ** 2 - .2523 * char_lvl + 14.74
    return mult_type_dict[react_type] * bonus_mult * lvl_mult * calc_resist(enemy_resist_pct)


def def_multiplier(char_lvl=80, enemy_lvl=90, def_reduction=0):
    return (char_lvl + 100) / ((1 - def_reduction) * (enemy_lvl + 100) + char_lvl + 100)


def incoming_damage(base_atk, atk_pct, flat_atk, atk_scaling, crit_rate, crit_damage, damage_bonus, char_lvl=80,
                    enemy_lvl=80, def_reduction=0, enemy_resist=0.1):
    return base_damage(calc_attack(base_atk, atk_pct, flat_atk), atk_scaling, damage_bonus) * \
           crit_multiplier(crit_rate, crit_damage) * \
           def_multiplier(char_lvl=char_lvl, enemy_lvl=enemy_lvl, def_reduction=def_reduction) * \
           calc_resist(enemy_resist)

def total_dmg_bonus(dmg_types, attributes):
    sum = 0
    for type in dmg_types:
        sum += attributes.dmg_bonus.get(type, 0)
    if DmgTag.ALL not in dmg_types:
        sum += attributes.dmg_bonus.get(DmgTag.ALL, 0)
    return sum

class Attributes:
    def __init__(self, base_atk=0, base_hp=0, base_def=0, atk_pct=0, flat_atk=0, crit_rate=0, crit_dmg=0,
                 er=0, em=0, hp_pct=0, flat_hp=0, def_pct=0, flat_def=0, dmg_bonus=None, reaction_bonus=None):
        self.base_atk = base_atk
        self.base_hp = base_hp
        self.base_def = base_def
        self.atk_pct = atk_pct
        self.flat_atk = flat_atk
        self.crit_rate = crit_rate
        self.crit_dmg = crit_dmg
        self.er = er
        self.em = em
        self.hp_pct = hp_pct
        self.flat_hp = flat_hp
        self.def_pct = def_pct
        self.flat_def = flat_def
        if dmg_bonus is None:
            self.dmg_bonus = dict()
        else:
            self.dmg_bonus = dmg_bonus
        if reaction_bonus is None:
            self.reaction_bonus = dict()
        else:
            self.reaction_bonus = reaction_bonus

    def __add__(self, o):
        base_atk = self.base_atk + o.base_atk
        base_hp = self.base_hp + o.base_hp
        base_def = self.base_def + o.base_def

        atk_pct = self.atk_pct + o.atk_pct
        flat_atk = self.flat_atk + o.flat_atk
        crit_rate = self.crit_rate + o.crit_rate
        crit_dmg = self.crit_dmg + o.crit_dmg
        er = self.er + o.er
        em = self.em + o.em
        hp_pct = self.hp_pct + o.hp_pct
        flat_hp = self.flat_hp + o.flat_hp
        def_pct = self.def_pct + o.def_pct
        flat_def = self.flat_def + o.flat_def
        dmg_bonus = add_dicts(self.dmg_bonus, o.dmg_bonus)
        reaction_bonus = add_dicts(self.reaction_bonus, o.reaction_bonus)
        return Attributes(base_atk=base_atk, base_hp=base_hp, base_def=base_def, atk_pct=atk_pct, flat_atk=flat_atk,
                          crit_rate=crit_rate, crit_dmg=crit_dmg, er=er, em=em, hp_pct=hp_pct, flat_hp=flat_hp,
                          def_pct=def_pct, flat_def=flat_def, dmg_bonus=dmg_bonus, reaction_bonus=reaction_bonus)

    def get(self, name):
        return self.__getattribute__(name)

    def set(self, name, value):
        return self.__setattr__(name, value)

    def __str__(self):
        ret = ''
        ret += f'Base ATK: {self.base_atk}\n'
        ret += f'Base HP: {self.base_hp}\n'
        ret += f'Base DEF: {self.base_def}\n'
        ret += f'ATK%: {self.atk_pct}\n'
        ret += f'Flat ATK: {self.flat_atk}\n'
        ret += f'CR: {self.crit_rate}\n'
        ret += f'CD: {self.crit_dmg}\n'
        ret += f'ER: {self.er}\n'
        ret += f'EM: {self.em}\n'
        ret += f'HP%: {self.hp_pct}\n'
        ret += f'Flat HP: {self.flat_hp}\n'
        ret += f'DEF%: {self.def_pct}\n'
        ret += f'Flat DEF: {self.flat_def}\n'
        ret += '\n'
        for tag, bonus in self.dmg_bonus.items():
            ret += f'{tag}: {bonus}\n'
        return ret

    def copy(self):
        return self + Attributes()


class DmgTag:
    PHYS = "PHYS"
    CRYO = "CRYO"
    PYRO = "PYRO"
    HYDRO = "HYDRO"
    ELECTRO = "ELECTRO"
    ANEMO = "ANEMO"
    GEO = "GEO"
    SKILL = "SKILL"  # elemental skill
    BURST = "BURST"  # elemental burst
    NORMAL = "NORMAL"  # normal attacks
    CHARGED = "CHARGED"  # charged attacks
    PLUNGE = "PLUNGE" # plunge attacks
    ALL = "ALL"


class ReactionType:
    OVERLOAD = "OVERLOAD"
    OL = "OVERLOAD"
    SHATTERED = "SHATTERED"
    SHATTER = "SHATTERED"
    ELECTROCHARGED = "ELECTROCHARGED"
    EC = "ELECTROCHARGED"
    SWIRL = "SWIRL"
    SUPERCONDUCT = "SUPERCONDUCT"
    SC = "SUPERCONDUCT"
    MELT = "MELT"
    VAPORIZE = "VAPORIZE"
    VAPE = "VAPORIZE"


class WeaponTypes:
    BOW = "BOW"
    SWORD = "SWORD"
    CLAYMORE = "CLAYMORE"
    POLEARM = "POLEARM"
    CATALYST = "CATALYST"


class Event:
    AFTER_SKILL = "SKILL"
    AFTER_BURST = "BURST"
    AFTER_NORMAL = "NORMAL"
    AFTER_CHARGED = "CHARGED"
    AFTER_KIll = "KILL"
    HAVE_SHIELD = "SHIELD"
    HIT_WEAKPOINT = "WEAK"
    ENERGY_FULL = "ENERGY_FULL"
    AMOS_STACKS = "AMOS"
    ALLEY_STACKS = "ALLEY"
    ENEMY_ELECTRO = "ELECTRO"
    ENEMY_PYRO = "PYRO"
    ENEMY_CRYO = "CRYO"
    ENEMY_FROZEN = "FROZEN"
    ENEMY_HYDRO = "HYDRO"

class Buffs:
    # TODO: idk
    BENNETT = "BENNETT"
    NOBLESSE = "NOBLESSE"
    KAZOO = "KAZOO"
    SUCROSE = "SUCROSE"
    TTDS = "TTDS"
    PYRO_RES = "PYRO_RES"
    CRYO_RES = "CRYO_RES"
    GEO_RES = "GEO_RES"