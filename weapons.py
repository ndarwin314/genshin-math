from utils import*
from abc import ABC, abstractmethod

class Weapon(ABC):
    attributes = Attributes()
    passive_effects = {}
    name = ""

    @abstractmethod
    def __init__(self, refinement=1):
        if refinement not in (1, 2, 3, 4, 5):
            raise ValueError("Must be int between 1 and 5 inclusive")
        self.refinement = refinement

    @abstractmethod
    def get_attributes(self, state):
        pass

    def __repr__(self):
        return f"{self.name} Refinement {self.refinement}"

class Bow(Weapon):
    type = WeaponTypes.BOW


class Sword(Weapon):
    type = WeaponTypes.SWORD


class Polearm(Weapon):
    type = WeaponTypes.POLEARM


class Claymore(Weapon):
    type = WeaponTypes.CLAYMORE


class Catalyst(Weapon):
    type = WeaponTypes.CATALYST


class AmosBow(Bow):
    passive_effects = {"stacks": 0}

    def __init__(self, refinement=1):
        super().__init__(refinement)
        dmgBonus = (9 + 3 * refinement) / 100
        self.name = "Amos Bow"
        self.attributes = Attributes(base_atk=608, atk_pct=0.496, dmg_bonus={DmgTag.CHARGED: dmgBonus,
                                                                             DmgTag.NORMAL: dmgBonus})

    def get_attributes(self, state, stacks=0):
        dmgBonus = stacks * (6 + 2 * self.refinement) / 100
        return self.attributes + Attributes(dmg_bonus={DmgTag.CHARGED: dmgBonus, DmgTag.NORMAL: dmgBonus})


class SkywardHarp(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        # idk how to include passive damage rn
        self.attributes = Attributes(base_atk=674, crit_rate=0.221, crit_dmg=0.15 + refinement * 0.05)
        self.name = "Skyward Harp"

    def get_attributes(self, state):
        return self.attributes


class ThunderingPulse(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=608, crit_dmg=0.662, atk_pct=0.15 + refinement * 0.05)
        self.name = "Thundering Pulse"

    def get_attributes(self, state, stacks=0):
        dmgBonus = [0, 12, 24, 40][stacks] * (self.refinement + 3) / 4
        return self.attributes + Attributes(dmg_bonus={DmgTag.NORMAL: dmgBonus})

class Elegy(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=608, er=0.551, em=45+15*refinement)
        self.name = "Elegy of the End"

    def get_attributes(self, state, passive_active=False):
        if passive_active:
            return self.attributes + Attributes(em=75+25*self.refinement, atk_pct=(0.15+self.refinement*0.05))
        return self.attributes


class CompoundBow(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        # does attack speed matter
        self.attributes = Attributes(base_atk=454, dmg_bonus={DmgTag.PHYS: 0.69})
        self.name = "Compound Bow"

    def get_attributes(self, state, stacks=0):
        return self.attributes + Attributes(atk_pct=stacks*(3+self.refinement))

class PrototypeCrescent(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=510, atk_pct=0.413)
        self.name = "Prototype Crescent"

    def get_attributes(self, state):
        return self.attributes + Attributes(atk_pct=state[Event.HIT_WEAKPOINT]*(0.27+0.09*self.refinement))


class Hamayumi(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        self.dmg_bonus = {DmgTag.NORMAL: (0.12 + 0.04 * refinement), DmgTag.CHARGED: (0.09 + 0.03 * refinement)}
        self.attributes = Attributes(base_atk=454, atk_pct=0.551, dmg_bonus=self.dmg_bonus)
        self.name = "Hamayumi"

    def get_attributes(self, state):
        if state[Event.ENERGY_FULL]:
            return self.attributes + Attributes(dmg_bonus=self.dmg_bonus)
        else:
            return self.attributes

class Mitternachts(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=510, dmg_bonus={DmgTag.PHYS: 0.517})
        self.name = "Mitternachts Waltz"

    def get_attributes(self, state):
        bonus = 0.16 + 0.04 * self.refinement
        return self.attributes + Attributes(dmg_bonus=
                                            {DmgTag.PHYS: 0.517, DmgTag.NORMAL: bonus * state[Event.AFTER_SKILL],
                                             DmgTag.SKILL: bonus * state[Event.AFTER_NORMAL]})


class WindblumeOde(Bow):
    def __init__(self, refinement=5):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=510, em=165)
        self.name = "Windblume Ode"

    def get_attributes(self, state):
        return self.attributes + Attributes(atk_pct=state[Event.AFTER_SKILL]*(0.12+0.04*self.refinement))

class AlleyHunter(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=565, atk_pct=0.276)
        self.name = "Alley Hunter"

    def get_attributes(self, state):
        stacks = state[Event.ALLEY_STACKS]
        stackValue = 0.015 + 0.005 * self.refinement
        return self.attributes + Attributes(dmg_bonus={DmgTag.ALL: stackValue * stacks})


class BlackcliffWarbow(Bow):
    def __init__(self, refinement=1, stacks=0):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=565, crit_dmg=0.368)
        self.name = "Blackcliff Warbow"

    def get_attributes(self, state, stacks=0):
        stackValue = 0.09 + 0.03 * self.refinement
        return self.attributes + Attributes(atk_pct=stackValue * stacks)


class ViridescentHunt(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        # passive :woozy:
        self.attributes = Attributes(base_atk=510, crit_rate=0.276)
        self.name = "Viridescent Hunt"

    def get_attributes(self, state):
        return self.attributes


class FavoniusWarbow(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=454, er=0.613)
        self.name = "Favonius Warbow"

    def get_attributes(self, state):
        return self.attributes


class SacrificialBow(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        self.attributes = Attributes(base_atk=565, er=0.306)
        self.name = "Sacrificial Bow"

    def get_attributes(self, state):
        return self.attributes

class Stringless(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        bonus = 0.18 + 0.06 * refinement
        self.attributes = Attributes(base_atk=510, em=165, dmg_bonus={DmgTag.BURST: bonus, DmgTag.SKILL: bonus})
        self.name = "The Stringless"

    def get_attributes(self, state):
        return self.attributes


class Rust(Bow):
    def __init__(self, refinement=1):
        super().__init__(refinement)
        bonus = 0.3 + 0.1 * refinement
        self.name = "Rust"
        self.attributes = Attributes(base_atk=510, atk_pct=0.413,
                                     dmg_bonus={DmgTag.CHARGED: -0.1, DmgTag.NORMAL: bonus})

    def get_attributes(self, state):
        return self.attributes
