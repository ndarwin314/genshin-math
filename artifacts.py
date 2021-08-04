from utils import*
from abc import ABC, abstractmethod



class ArtifactSet:
    GLAD = "GLADIATOR'S FINALE"
    WANDERER = "WANDERER'S TROUPE"
    TS = "THUNDERSOOTHER"
    TF = "THUNDERING FURY"
    MAIDEN = "MAIDEN'S BELOVED"
    VV = "VIRIDESCENT VENERER"
    CW = "CRIMSON WITCH OF FLAMES"
    LW = "LAVAWALKER"
    NO = "NOBLESEE OBLIGE"
    BLOODSTAINED = "BLOODSTAINED CHIVALRY"
    AP = "ARCHAIC PETRA"
    BOLIDE = "RETRACTING BOLIDE"
    HOD = "HEART OF DEPTH"
    BS = "BLIZZARD STRAYER"
    TOM = "TENACITY OF THE MILLELITH"
    PF = "PALE FLAME"
    EMBLEM = "EMBLEM OF SEVERED FATE"
    SR = "SHIMENAWA'S REMINISCENCE"

class Artifact:

    def __init__(self, artifact_sets):
        total = 0
        self.attributes = Attributes()
        for artifact, quantity in artifact_sets.items():
            total += quantity
            if quantity >= 2:
                if artifact == ArtifactSet.GLAD or artifact == ArtifactSet.SR:
                    self.attributes.atk_pct += 0.18
                elif artifact == ArtifactSet.WANDERER:
                    self.attributes.em += 80
                elif artifact == ArtifactSet.TF:
                    self.attributes.dmg_bonus[DmgTag.ELECTRO] = 0.15
                elif artifact == ArtifactSet.VV:
                    self.attributes.dmg_bonus[DmgTag.ANEMO] = 0.15
                elif artifact == ArtifactSet.CW:
                    self.attributes.dmg_bonus[DmgTag.PYRO] = 0.15
                elif artifact == ArtifactSet.NO:
                    self.attributes.dmg_bonus[DmgTag.BURST] = 0.2
                elif artifact == ArtifactSet.BLOODSTAINED or artifact == ArtifactSet.PF:
                    self.attributes.dmg_bonus.setdefault(DmgTag.PHYS, 0)
                    self.attributes.dmg_bonus[DmgTag.PHYS] += 0.25
                elif artifact == ArtifactSet.AP:
                    self.attributes.dmg_bonus[DmgTag.GEO] = 0.15
                elif artifact == ArtifactSet.BS:
                    self.attributes.dmg_bonus[DmgTag.CRYO] = 0.15
                elif artifact == ArtifactSet.HOD:
                    self.attributes.dmg_bonus[DmgTag.HYDRO] = 0.15
                elif artifact == ArtifactSet.TOM:
                    self.attributes.hp_pct = 0.2
                elif artifact == ArtifactSet.EMBLEM:
                    self.attributes.er = 0.2
            if quantity >= 4:
                if artifact == ArtifactSet.GLAD:
                    # this doesn't check if the weapon type is correct to get the bonus
                    self.attributes.dmg_bonus[DmgTag.NORMAL] = 0.35
                elif artifact == ArtifactSet.WANDERER:
                    self.attributes.dmg_bonus[DmgTag.CHARGED] = 0.35
                elif artifact == ArtifactSet.TF:
                    self.attributes.reaction_bonus[ReactionType.OL] = 0.4
                    self.attributes.reaction_bonus[ReactionType.EC] = 0.4
                    self.attributes.reaction_bonus[ReactionType.SC] = 0.4
                elif artifact == ArtifactSet.VV:
                    self.attributes.reaction_bonus[ReactionType.SWIRL] = 0.6
                elif artifact == ArtifactSet.CW:
                    self.attributes.reaction_bonus[ReactionType.OL] = 0.4
                    self.attributes.reaction_bonus[ReactionType.MELT] = 0.15
                    self.attributes.reaction_bonus[ReactionType.VAPE] = 0.15

        if total >= 5:
            raise ValueError("to much set bonus")
        self.sets = artifact_sets

    def get_attributes(self, state, enemy):
        modifiers = Attributes()
        for artifact, quantity in self.sets.items():
            if quantity >= 4:
                if artifact == ArtifactSet.TS and enemy[Event.ENEMY_ELECTRO]:
                    modifiers.dmg_bonus[DmgTag.ALL] = 0.35
                elif artifact == ArtifactSet.CW and state[Event.AFTER_SKILL]:
                    modifiers.dmg_bonus[DmgTag.PYRO] += 0.075 * max(3, state[Event.AFTER_SKILL])
                elif artifact == ArtifactSet.LW and state[Event.ENEMY_PYRO]:
                    modifiers.dmg_bonus[DmgTag.ALL] = 0.35
                elif artifact == ArtifactSet.BLOODSTAINED and state[Event.AFTER_KIll]:
                    modifiers.dmg_bonus[DmgTag.CHARGED] = 0.5
                elif artifact == ArtifactSet.AP:
                    pass
                    # add something for crystallize shield
                elif artifact == ArtifactSet.BOLIDE and state[Event.HAVE_SHIELD]:
                    modifiers.dmg_bonus[DmgTag.CHARGED] = 0.4
                    modifiers.dmg_bonus[DmgTag.NORMAL] = 0.4
                elif artifact == ArtifactSet.BS and enemy[Event.ENEMY_CRYO]:
                    modifiers.crit_rate = 0.2
                    if state[Event.ENEMY_FROZEN]:
                        modifiers.crit_rate += 0.2
                elif artifact == ArtifactSet.HOD and state[Event.AFTER_SKILL]:
                    modifiers.dmg_bonus[DmgTag.CHARGED] = 0.3
                    modifiers.dmg_bonus[DmgTag.NORMAL] = 0.3
                elif artifact == ArtifactSet.PF and state[Event.AFTER_SKILL]:
                    stacks = state.Event.AFTER_SKILL
                    modifiers.atk_pct += 0.09 * max(2, stacks)
                    if stacks >= 2:
                        modifiers.dmg_bonus[DmgTag.PHYS] += 0.25
                elif artifact == ArtifactSet.EMBLEM:
                    # TODO: dumb er bonus to burst
                    modifiers.dmg_bonus[DmgTag.BURST] = 0.3
                elif artifact == ArtifactSet.SR and state[Event.AFTER_SKILL]:
                    modifiers.dmg_bonus[DmgTag.NORMAL] = 0.5
                    modifiers.dmg_bonus[DmgTag.CHARGED] = 0.5
                    modifiers.dmg_bonus[DmgTag.PLUNGE] = 0.5
        return modifiers + self.attributes

    def __repr__(self):
        repr = ""
        for k,v in self.sets.items():
            repr += f"{k} {v},"
        return repr[:-1]
