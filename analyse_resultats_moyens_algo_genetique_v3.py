import matplotlib.pyplot as plt
from time import monotonic
from collections import deque

def calculer_ao(lValeurs, lAO):
    nbAO = sum(1 if ao <= len(lValeurs) or ao == float("inf") else 0 for ao in lAO)
    lAOValeurs = [[0]*len(lValeurs) for i in range(nbAO)]
    lValeursAO = [deque([]) for i in range(nbAO)]
    lSommeValeursAO = [0]*nbAO
    for i, valeur in enumerate(lValeurs):
        for iAO in range(nbAO):
            lSommeValeursAO[iAO] += valeur
            if lAO[iAO] == float("inf"):
                lAOValeurs[iAO][i] = lSommeValeursAO[iAO] / (i+1)
            else :
                lValeursAO[iAO].append(valeur)
                if len(lValeursAO[iAO]) == lAO[iAO]:
                    lAOValeurs[iAO][i] = lSommeValeursAO[iAO] / lAO[iAO]
                    lSommeValeursAO[iAO] -= lValeursAO[iAO].popleft()
                else :
                    lAOValeurs[iAO][i] = lSommeValeursAO[iAO] / (i+1)
    return lAOValeurs

NN = True
GA = True
NES = False
DRL = False
assert (GA and NN) and not NES and not DRL #car pas implémentés

lAO = [float("inf"), 100, 1000, 10000]

if GA :
    if NN :
        lFichiers = ["lScores_GA_NN.txt", "lNbCoups_GA_NN.txt", "lDicoReseau_GA_NN.txt"]
    else :
        lFichiers = ["lScores.txt", "lNbCoups.txt", "lConstantes.txt"]
elif NES :
    lFichiers = ["lScoresMoyensTotal_NES.txt", "lNbCoupsMoyensTotal_NES.txt", "lLMeilleursConstantesTotal_NES.txt"]
elif DRL :
    lFichiers = ["lScores_DRL.txt", "lNbCoups_DRL.txt", "lConstantes_DRL.txt"]

with open(lFichiers[0], "r") as fichier:
    lScores = eval(fichier.read())
    iMax = max(i if score is not None else 0 for i, score in enumerate(lScores))
    assert iMax >= 0
    if GA : 
        lScoresIndividus = list(map(list, zip(*lScores[:iMax+1])))
    if NES :
        lScoresMax = [scoreMoyen[0] for scoreMoyen in lScores]
        lScoresMoyens = [scoreMoyen[1] for scoreMoyen in lScores]
    elif DRL :
        lScores = [score if score is not None else 0 for score in lScores]
        lAOScores = calculer_ao(lScores, lAO)

with open(lFichiers[1], "r") as fichier:
    lNbCoups = eval(fichier.read())
    iMax = max(i if nbCoups is not None else 0 for i,nbCoups in enumerate(lNbCoups))
    assert iMax >= 0
    if GA : 
        lNbCoupsIndividus = list(map(list, zip(*lNbCoups[:iMax+1])))
    if NES :
        lNbCoupsMax = [nbCoupsMoyen[0] for nbCoupsMoyen in lNbCoups]
        lNbCoupsMoyenne = [nbCoupsMoyen[1] for nbCoupsMoyen in lNbCoups]
    elif DRL :
        lNbCoups = [nbCoups if nbCoups is not None else 0 for nbCoups in lNbCoups]
        lAONbCoups = calculer_ao(lNbCoups, lAO)

with open(lFichiers[2], "r") as fichier:
    if (GA and not NN) or NES :
        lConstantes = eval(fichier.read())
        lConstantes = [list(liste) for liste in zip(*lConstantes)] #[[combinaison[i] for combinaison in lConstantes] for i in range(len(lConstantes[0]))]
        lNomsConstantes = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta"]

lGenerations = list(range(1, iMax+2))

fig,(axe1,axe2,axe3) = plt.subplots(3, 1)
axe1.set_position([0.1, 0.7, 0.7, 0.2])
axe2.set_position([0.1, 0.4, 0.7, 0.2])
axe3.set_position([0.1, 0.1, 0.7, 0.2])

if GA :
    for i, lScores in enumerate(lScoresIndividus):
        c = (i+1) / len(lScoresIndividus)
        titre = "lScoresMax" if i==0 else "lScoresMin" if i==len(lScoresIndividus)-1 else ""
        axe1.plot(lGenerations, lScores, label=titre, color=(c, 1-c, (2*c)%1))
elif NES :
    axe1.plot(lGenerations, lScoresMax, label="lScoresMax", color=(0,0.8,0))
    axe1.plot(lGenerations, lScoresMoyens, label="lScoresMin", color=(0.8,0,0))
elif DRL :
    axe1.plot(lGenerations, lScores, label="score", color=(0.8,0,0))
    for i, (ao, lY) in enumerate(zip(lAO, lAOScores)):
        c = i/len(lAOScores)
        axe1.plot(lGenerations, lY, label=f"ao {ao}", color=(0.1+c/2, c, 1-c))
axe1.legend(loc="center left", bbox_to_anchor=(1, 0.5))

if GA :
    for i, lNbCoups in enumerate(lNbCoupsIndividus):
        c = (i+1) / len(lNbCoupsIndividus)
        titre = "lNbCoupsMax" if i==0 else "lNbCoupsMin" if i==len(lNbCoupsIndividus)-1 else ""
        axe2.plot(lGenerations, lNbCoups, label=titre, color=(c, 1-c, (2*c)%1))
elif NES:
    axe2.plot(lGenerations, lNbCoupsMax, label="lNbCoupsMax", color=(0,0.8,0))
    axe2.plot(lGenerations, lNbCoupsMoyenne, label="lNbCoupsMin", color=(0.8,0,0))
elif DRL:
    axe2.plot(lGenerations, lNbCoups, label="nb coups", color=(0.8,0,0))
    for i, (ao, lY) in enumerate(zip(lAO, lAONbCoups)):
        c = i/len(lAONbCoups)
        axe2.plot(lGenerations, lY, label=f"ao {ao}", color=(0.1+c/2, c, 1-c))
axe2.legend(loc="center left", bbox_to_anchor=(1, 0.5))

if (GA and not NN) or NES :
    for i in range(len(lConstantes)):
        c = i/len(lConstantes)
        axe3.plot(lGenerations, lConstantes[i], label=lNomsConstantes[i], color=(c, 1-c, (2*c)%1))
    axe3.set_ylim(-1.1, 1.1)
    axe3.legend(loc="center left", bbox_to_anchor=(1, 0.5))

plt.show()