import random
import bisect
import numpy as np
import matplotlib.pyplot as plt


characterProbability = [0]
for i in range(1, 76):
    characterProbability.append(0.006 * pow(0.994, i - 1) + characterProbability[-1])
for i in range(76, 90):
    # (1 - characterProbability[75]) gives the probability 5* was in the first 75 wishes
    # we use this to scale our new geometric distribution so the total distribution sums to 1
    characterProbability.append(
        (1 - characterProbability[75]) * .323 * pow(.677, i - 76) + characterProbability[-1])
characterProbability.append(1)

weaponProbability = [0]
for i in range(1, 63):
    weaponProbability.append(0.007 * pow(0.993, i - 1) + weaponProbability[-1])
for i in range(63, 76):
    weaponProbability.append((1 - characterProbability[63]) * 0.2 * pow(0.8, i - 63) + weaponProbability[-1])
weaponProbability.append(1)

def sim_gacha(constellation=0, bannerCharacterEnsured=False):
    totalWishes = 0
    totalBannerFives = 0
    while totalBannerFives != 1 + constellation:
        r = random.random()
        sinceLast = bin_search(r, characterProbability)
        totalWishes += sinceLast
        if bannerCharacterEnsured:
            totalBannerFives += 1
            bannerCharacterEnsured = False
        else:
            if random.random() < 0.5:
                totalBannerFives += 1
                bannerCharacterEnsured = False
            else:
                bannerCharacterEnsured = True
    return totalWishes


def simulate_weapon():
    totalWishes = 0
    fiveStarProbability = 0.75
    undesiredFiveStar = 0
    guarantee = False
    while True:
        r = random.random()
        pity = bin_search(r, weaponProbability)
        totalWishes += pity
        if undesiredFiveStar == 2:
            return totalWishes
        else:
            r = random.random() * fiveStarProbability ** guarantee
            undesiredFiveStar += 1
            if r < fiveStarProbability / 2:
                return totalWishes
            if r > fiveStarProbability:
                guarantee = True


def bin_search(value, array):
    return bisect.bisect_left(array, value)


def character():
    trials = 10 ** 5
    constellation = 0
    banner = False
    rolls = [sim_gacha(constellation, banner) for _ in range(trials)]
    average = sum(rolls) / trials
    Min = min(rolls)
    Max = max(rolls)
    variance = sum([(i - average) ** 2 for _ in rolls]) / (trials - 1)
    rolls.sort()
    np.savetxt("results.txt", np.array(rolls, dtype=int), fmt="%i")
    print(f"After simulating {trials} attempts too get the banner character to constellation {constellation} "
          f"starting {'with' + 'out' * (not banner)} 50/50:")
    print(f"    Average: {average}")
    print(f"    Minimum rolls: {Min}")
    print(f"    Maximum rolls: {Max}")
    print(f"    Standard Deviation: {variance ** (1 / 2)}")
    print(f"    Median: {rolls[trials // 2]}")
    print(f"    First Quartile: {rolls[trials // 4]}")
    print(f"    Third Quartile: {rolls[3 * trials // 4]}")
    print(f"    10th Percentile: {rolls[trials // 10]}")
    print(f"    90th Percentile: {rolls[9 * trials // 10]}")
    plt.hist(rolls, bins=Max, density=True)
    plt.xlabel("Number of wishes")
    plt.ylabel("Probability")
    plt.title("5* character without guarantee")
    plt.axis([0, 180, 0, 0.150])
    plt.grid(True)
    plt.show()


def weapon(trials=10 ** 7):
    rolls = [simulate_weapon() for _ in range(trials)]
    rolls.sort()
    Min = rolls[0]
    Max = rolls[-1]
    average = sum(rolls) / trials
    variance = sum([(i - average) ** 2 for i in rolls]) / (trials - 1)
    print(f"    Average: {average}")
    print(f"    Minimum rolls: {Min}")
    print(f"    Maximum rolls: {Max}")
    print(f"    Standard Deviation: {variance ** (1 / 2)}")
    print(f"    Median: {rolls[trials // 2]}")
    print(f"    First Quartile: {rolls[trials // 4]}")
    print(f"    Third Quartile: {rolls[3 * trials // 4]}")
    print(f"    10th Percentile: {rolls[trials // 10]}")
    print(f"    90th Percentile: {rolls[9 * trials // 10]}")
    print(f"    95th Percentile: {rolls[19 * trials // 20]}")
    print(f"    99th Percentile: {rolls[99 * trials // 100]}")
    plt.hist(rolls, bins=Max, density=True)
    plt.xlabel("Number of wishes")
    plt.ylabel("Probability")
    plt.title("Number of wishes to get desired 5 star weapon")
    plt.axis([0, 220, 0, 0.06])
    plt.grid(True)
    plt.show()