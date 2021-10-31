from abc import ABC

from weapons import*
from artifacts import*


class Character(ABC):
    # assuming talent level 9 on all talents for simplicity
    weaponType = WeaponTypes
    element = DmgTag
    substat_rolls = {"atk_pct": 0.04955,
                     "flat_atk": 16.535,
                     "crit_rate": 0.03305,
                     "crit_dmg": 0.0661,
                     "em": 19.815}

    er_roll = 0.5505



    @abstractmethod
    def __init__(self, weapon, artifact_set, buffs=(), constellation=1):
        # idk how type hints work
        self.attributes = Attributes()
        self.constellation = constellation
        self.weapon = weapon
        self.state = {Event.AFTER_BURST: False,
                      Event.AFTER_CHARGED: False,
                      Event.AFTER_NORMAL: False,
                      Event.AFTER_SKILL: False,
                      Event.AFTER_KIll: False,
                      Event.HAVE_SHIELD: False,
                      Event.HIT_WEAKPOINT: False,
                      Event.ENERGY_FULL: False,
                      Event.ALLEY_STACKS: 0,
                      Event.AMOS_STACKS: 0}
        self.enemy = {Event.ENEMY_CRYO: False,
                      Event.ENEMY_FROZEN: False,
                      Event.ENEMY_PYRO: False,
                      Event.ENEMY_ELECTRO: False,
                      Event.ENEMY_HYDRO: False}
        self.sets = artifact_set
        self.artifact_attributes = Attributes()
        if Buffs.BENNETT in buffs:
            self.attributes.flat_atk += 1093
        if Buffs.NOBLESSE in buffs:
            self.attributes.atk_pct += 0.2
        if Buffs.KAZOO in buffs:
            # currently assuming 1000 em
            # also this is bad
            self.attributes.dmg_bonus[DmgTag.CRYO] = 0.4
            self.attributes.dmg_bonus[DmgTag.PYRO] = 0.4
            self.attributes.dmg_bonus[DmgTag.HYDRO] = 0.4
            self.attributes.dmg_bonus[DmgTag.ELECTRO] = 0.4
            # c2 kekW
            #self.attributes.em += 200
        if Buffs.SUCROSE in buffs:
            # currently assuming 750 em
            self.attributes.em += 200

        if Buffs.TTDS in buffs:
            self.attributes.atk_pct += 0.48
        if Buffs.PYRO_RES in buffs:
            self.attributes.atk_pct += 0.25
        if Buffs.CRYO_RES in buffs:
            # TODO: idk
            pass
        if Buffs.GEO_RES in buffs:
            self.attributes.dmg_bonus[DmgTag.ALL] = 0.15

    @abstractmethod
    def normal_attack(self, number_of_hits):
        self.state[Event.AFTER_NORMAL] = True

    @abstractmethod
    def charged_attack(self):
        self.state[Event.AFTER_CHARGED] = True

    @abstractmethod
    def elemental_skill(self):
        self.state[Event.AFTER_SKILL] = True

    @abstractmethod
    def elemental_burst(self):
        self.state[Event.AFTER_BURST] = True

    @abstractmethod
    def damage_rotation(self):
        pass

    def attr(self, **kwags):
        base = self.attributes + self.sets.get_attributes(self.state, self.enemy) + self.artifact_attributes
        # TODO: maybe add some kind of verification to stacks but i am very lazy
        if isinstance(self.weapon, AmosBow):
            return base + self.weapon.get_attributes(self.state, kwags.get('amos_stacks', 0))
        elif isinstance(self.weapon, CompoundBow):
            return base + self.weapon.get_attributes(self.state, kwags.get('compound_stacks', 0))
        elif isinstance(self.weapon, BlackcliffWarbow):  # add other blackcliff weapons
            return base + self.weapon.get_attributes(self.state, kwags.get('blackcliff_stacks', 0))
        return base + self.weapon.get_attributes(self.state)

    # main_stats should be list of main stats of sands, goblet, circlet
    # TODO: bad
    def optimize_artifacts(self, total_rolls=20, er_requirement=0):
        self.artifact_attributes.flat_atk += 311
        self.artifact_attributes.flat_hp += 4780
        #self.artifact_attributes.em += 187
        self.artifact_attributes.atk_pct = 0.466
        self.artifact_attributes.dmg_bonus[self.element] = 0.466
        self.artifact_attributes.crit_rate = 0.311
        while self.attr().er < er_requirement:
            total_rolls -= 1
            self.artifact_attributes.er += self.er_roll
        for i in range(total_rolls):
            maxDamage = 0
            best = ""
            oldStat = 0
            for sub, roll in self.substat_rolls.items():
                oldValue = self.artifact_attributes.__getattribute__(sub)
                self.artifact_attributes.__setattr__(sub, roll + oldValue)
                newDamage = self.damage_rotation()
                if newDamage > maxDamage:
                    maxDamage = newDamage
                    best = sub
                    oldStat = oldValue
                self.artifact_attributes.__setattr__(sub, oldValue)

            self.artifact_attributes.__setattr__(best, self.substat_rolls[best] + oldStat)
        #print(self.attr())
        """k = len(self.substat_rolls)
        partitions = fast_comb(total_rolls, k)
        original = self.artifact_attributes.copy()
        maxDamage = 0
        best = 0
        for partition in partitions:
            self.assign_substats(partition, total_rolls, k)
            newDamage = self.damage_rotation()
            if newDamage > maxDamage:
                maxDamage = newDamage
                best = partition
            self.artifact_attributes = original
        
        self.assign_substats(best, total_rolls, k)
        print(best)"""


    def reset(self):
        for event in self.state:
            self.state[event] = False
        for event in self.enemy:
            self.enemy[event] = False

    def set_aura(self, element):
        for event in self.enemy:
            self.enemy[event] = False
        self.enemy[element] = True

    def assign_substats(self, partition, total_rolls, k):
        i = 0
        for sub, roll in self.substat_rolls.items():
            if i != k - 1:
                self.artifact_attributes.set(sub, self.artifact_attributes.get(sub) + roll * (partition[i + 1] - partition[i]))
            else:
                self.artifact_attributes.set(sub, self.artifact_attributes.get(sub) + roll * (total_rolls - partition[k - 1]))
            i += 1

# noinspection PyTypeChecker
class Ganyu(Character):
    weaponType = WeaponTypes.BOW
    element = DmgTag.CRYO

    def __init__(self, weapon, artifact_set, buffs=(), constellation=1):
        attributes = Attributes(base_atk=335, base_def=630, base_hp=9797, crit_dmg=0.884, crit_rate=0.05)
        super().__init__(weapon, artifact_set, buffs=buffs, constellation=constellation)
        self.set_a1(False)
        self.attributes += attributes

    def normal_attack(self, number_of_hits):
        super().normal_attack(0)
        damageType = [DmgTag.PHYS, DmgTag.NORMAL]
        normal_attack_values = [0.583, 1.237, 2.073, 2.909, 3.795, 4.855]
        # TODO: make this work, not high priority since ganyu normals are omegalul
        return normal_attack_values[number_of_hits - 1], damageType

    def charged_attack(self, fully_charged=True, bloom=True, hit_weakpoint=False, amos_stacks=1, **kwargs):
        damageType = [DmgTag.CHARGED]
        bonus = Attributes(crit_rate=0.2 * self.get_a1() * fully_charged)
        if not fully_charged:
            damageType += [DmgTag.NORMAL]
            scaling = 0.806
        else:
            self.set_a1(True)
            damageType += [DmgTag.CRYO]
            if not bloom:
                scaling = 2.11
            else:
                damage = outgoing_damage(self.attr(amos_stacks=amos_stacks) + bonus, 2.18, damageType, self.enemy) + \
                       outgoing_damage(self.attr(amos_stacks=amos_stacks+3) + bonus, 3.7, damageType, self.enemy)
                self.state[Event.HIT_WEAKPOINT] = hit_weakpoint
                super().charged_attack()
                return damage

        damage = outgoing_damage(self.attr() + bonus, scaling, damageType, self.enemy)
        self.state[Event.HIT_WEAKPOINT] = hit_weakpoint
        super().charged_attack()
        return damage

    def elemental_burst(self, number_of_hits=10):
        # i think 1 icicle hits aims at a target approx every 1.5 seconds
        # specifically 1 icicle drops every .3 seconds, with an icicle targeting an enemy if the previous 4 didn't
        # with grouping the total number of hits grows quadratically
        super().elemental_burst()
        damage_type = [DmgTag.BURST, DmgTag.CRYO]
        icicle_scaling = 1.19
        damage = outgoing_damage(self.attr(), icicle_scaling, damage_type, self.enemy)
        super().elemental_burst()
        return damage

    def elemental_skill(self, second_hit=True):
        damageType = [DmgTag.SKILL, self.element]
        if second_hit:
            scaling = 4.28
        else:
            scaling = 2.04
        damage = outgoing_damage(self.attr(), scaling, damageType, self.enemy)
        super().elemental_skill()
        return damage

    def set_a1(self, truth):
        self.state["a1"] = truth

    def get_a1(self):
        return self.state["a1"]

    def damage_rotation(self):
        total_damage = 0
        total_damage += self.elemental_skill()
        self.set_aura(DmgTag.PYRO)
        self.state[Event.ENERGY_FULL] = True
        for i in range(4):
            total_damage += self.charged_attack(hit_weakpoint=True)
        self.reset()
        return total_damage

    def optimize_artifacts(self, substat_rolls=20, er_requrements=0):
        super().optimize_artifacts(substat_rolls, er_requrements)

    def attr(self, **kwargs):
        return super().attr(**kwargs)

class Fischl(Character):
    # TODO: something about fischl A4 and C6

    weaponType = WeaponTypes.BOW
    element = DmgTag.ELECTRO

    def __init__(self, weapon, artifact_set, buffs=(), constellation=1):
        attributes = Attributes(base_atk=244, base_def=594, base_hp=9189, crit_dmg=0.5, crit_rate=0.05, atk_pct=0.24)
        super().__init__(weapon, artifact_set, buffs=buffs, constellation=constellation)
        self.attributes += attributes

    def normal_attack(self, number_of_hits):
        super().normal_attack(0)
        damageType = [DmgTag.PHYS, DmgTag.NORMAL]
        normal_attack_values = [0.811, 0.86, 2.073, 1.07, 1.06, 1.32]
        total_damage = 0
        for i in range(number_of_hits):
            total_damage += outgoing_damage(self.attr(), normal_attack_values, damageType, self.enemy)
            # this could be optimized but i dont think it matters
            # does this work if oz is on field, unclear
            if self.constellation >= 1:
                total_damage += outgoing_damage(self.attr(), 0.22, damageType, self.enemy)
            self.state[Event.AFTER_NORMAL] += 1

        return total_damage

    def charged_attack(self, fully_charged=True):
         # i don't fucking care about fischl A1
        damageType = [DmgTag.CHARGED]
        if not fully_charged:
            damageType += [DmgTag.NORMAL]
            scaling = 0.806
        else:
            damageType += [self.element]
            scaling = 2.11
        damage = outgoing_damage(self.attr(), scaling, damageType, self.enemy)
        super().charged_attack()
        return damage

    def elemental_skill(self):
        damageType = [DmgTag.SKILL, self.element]
        totalDamage = 0
        summoning_damage = 2 if self.constellation >= 2 else 0
        summoning_damage += 2.31 if self.constellation >= 3 else 1.96
        totalDamage += outgoing_damage(self.attr(), summoning_damage, damageType, self.enemy)
        super().elemental_skill()
        """for i in range(9+2*(self.constellation >= 6)):
            # this might not be accurate because of snapshotting
            oz_scaling = 1.78 if (self.constellation >= 3) else 1.51
            totalDamage += outgoing_damage(self.attr(), oz_scaling, damageType, self.enemy)"""
        oz_scaling = 1.78 if (self.constellation >= 3) else 1.51
        # this should work since oz snapshots so damage on each shot is the same

        totalDamage += (9 + 2 * (self.constellation >= 6)) * \
                       outgoing_damage(self.attr(), oz_scaling, damageType, self.enemy)
        self.state[Event.AFTER_SKILL] = False
        return totalDamage

    def elemental_burst(self):
        damageType = [DmgTag.BURST, self.element]
        totalDamage = 0
        if self.constellation >= 4:
            totalDamage += outgoing_damage(self.attr(), 2.22, damageType, self.enemy)
        talent_scaling = 4.16 if (self.constellation >= 3) else 3.54
        totalDamage += outgoing_damage(self.attr(), talent_scaling, damageType, self.enemy)
        super().elemental_burst()
        damageType = [DmgTag.SKILL, self.element]
        oz_scaling = 1.78 if (self.constellation >= 3) else 1.51
        totalDamage += (9 + 2 * (self.constellation >= 6)) * \
                       outgoing_damage(self.attr(), oz_scaling, damageType, self.enemy)
        self.state[Event.AFTER_BURST] = False
        return totalDamage

    def a4_passive(self):
        pass

    def damage_rotation(self):
        self.state[Event.ALLEY_STACKS] = 10
        total_damage = 0
        total_damage += self.elemental_skill()
        #total_damage += self.elemental_burst()
        self.reset()
        return total_damage

