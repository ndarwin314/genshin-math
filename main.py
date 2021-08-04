from characters import*
from weapons import*
from artifacts import*


if __name__ == '__main__':

    """weapons = [AmosBow(), ThunderingPulse(), SkywardHarp(), PrototypeCrescent(refinement=5), Hamayumi(refinement=5), WindblumeOde(), ViridescentHunt()]
    artifact_sets = [Artifact({ArtifactSet.SR: 4}), Artifact({ArtifactSet.WANDERER: 4})]
    buffs = (Buffs.BENNETT, Buffs.NOBLESSE, Buffs.KAZOO)
    for weapon in weapons:
        for set in artifact_sets:
            test = Ganyu(weapon, set, buffs=())
            print(f"{weapon} , {set}")
            test.optimize_artifacts(20)
            print(test.damage_rotation())"""

    weapons = [ThunderingPulse(), SkywardHarp(), Hamayumi(refinement=5), WindblumeOde(), Rust(),
               ViridescentHunt(), Stringless(), AlleyHunter(), Stringless(refinement=5), AlleyHunter(refinement=5)]
    artifact_sets = [Artifact({ArtifactSet.TF: 2, ArtifactSet.GLAD: 2})]
    buffs = (Buffs.BENNETT, Buffs.NOBLESSE)
    for weapon in weapons:
        for set in artifact_sets:
            test = Fischl(weapon, set, buffs=(), constellation=6)
            print(f"{weapon} , {set}")
            test.optimize_artifacts(20)
            print(test.damage_rotation())



