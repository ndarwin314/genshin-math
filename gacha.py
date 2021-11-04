import random
import bisect
import numpy as np
import time
import matplotlib.pyplot as plt
import multiprocessing as mp
import os

rampRate = 0.06
P = 0.006

"""characterProbability = [0]
for i in range(1, 74):
    characterProbability.append(P * pow(1-P, i - 1) + characterProbability[-1])
for i in range(74, 90):
    # (1 - characterProbability[75]) gives the probability 5* was in the first 75 wishes
    # we use this to scale our new geometric distribution so the total distribution sums to 1
    characterProbability.append(
        (1 - characterProbability[-1]) * (P+rampRate*(i-73)) + characterProbability[-1])
characterProbability.append(1)

weaponProbability = [0]
for i in range(1, 63):
    weaponProbability.append(0.007 * pow(0.993, i - 1) + weaponProbability[-1])
for i in range(63, 76):
    weaponProbability.append((1 - characterProbability[63]) * 0.2 * pow(0.8, i - 63) + weaponProbability[-1])
weaponProbability.append(1)"""

def deterministic(constellations=0, wishes=0):
    base = np.zeros((91,))
    base[0] = 0
    base[1:74] = P
    base[90] = 1
    for i in range(74, 90):
        base[i] = P + rampRate * (i-73)
    ones = np.ones((91,))
    temp = ones - base
    basePDF = np.zeros((91,))
    for i in range(91):
        basePDF[i] = np.prod(temp[0:i]) * base[i]
    doublePDF = np.zeros((181,))
    doublePDF[0:91] += basePDF
    for i in range(1, 90):
        doublePDF[i:i+91] += basePDF[i]*basePDF
    doublePDF *= 0.5
    fullPDF = doublePDF
    for i in range(constellations):
        fullPDF = np.convolve(fullPDF, doublePDF)
    maxValue = fullPDF.max(initial=0)
    print(fullPDF.cumsum()[wishes])
    plt.plot(fullPDF)
    plt.axis([0, (constellations+1)*180, 0, maxValue*1.1])
    plt.grid(True)
    plt.show()






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


def multiple(n):

    return [sim_gacha(n[1], n[2]) for _ in range(n[0])]


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

def get_mode_sorted(list):
    currentMode = 1
    modeCount = 0
    previous = 0
    currentCount = 0
    for i in list:
        if i == previous:
            currentCount += 1
        else:
            if currentCount > modeCount:
                modeCount = currentCount
                currentMode = previous
            currentCount = 1
        previous = i
    return modeCount

def character(constellation=0, trials=10 ** 5, banner=False):
    start = time.time()
    coreCount = os.cpu_count() - 1
    #rolls = [sim_gacha(constellation, banner) for _ in range(trials)]

    """with mp.Pool() as pools:
        rolls = pools.map(kill_me, iterable=zip([constellation]*trials, [banner]*trials))"""

    perCore = trials // coreCount
    with mp.Pool() as pools:
        temp = pools.map(multiple, iterable=zip([perCore]*coreCount,[constellation]*coreCount, [banner]*coreCount))
    rolls = [i for j in temp for i in j]

    average = sum(rolls) / trials
    variance = np.var(rolls)
    rolls.sort()
    Min = rolls[0]
    Max = rolls[-1]
    maxProbability = get_mode_sorted(rolls) / trials
    #np.savetxt("results.txt", np.array(rolls, dtype=int), fmt="%i")
    test = []
    for i in range(1, 91):
        test.append(rolls.count(i)/(perCore*coreCount))
    np.savetxt("results2.txt", np.array(test, dtype=float))
    print(f"After simulating {trials} attempts too get the banner character to constellation {constellation} "
          f"starting {'with' + 'out' * (not banner)} 50/50 to start:")
    print(f"    Average: {average}")
    print(f"    Minimum rolls: {Min}")
    print(f"    Maximum rolls: {Max}")
    print(f"    Standard Deviation: {variance ** (1 / 2)}")
    print(f"    Median: {rolls[trials // 2]}")
    print(f"    First Quartile: {rolls[trials // 4]}")
    print(f"    Third Quartile: {rolls[3 * trials // 4]}")
    print(f"    10th Percentile: {rolls[trials // 10]}")
    print(f"    90th Percentile: {rolls[9 * trials // 10]}")
    print(time.time()-start)

    plt.hist(rolls, bins=Max, density=True)
    plt.xlabel("Number of wishes")
    plt.ylabel("Probability")
    plt.title("5* character without guarantee")
    plt.axis([0, Max, 0, maxProbability * 1.2])
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
