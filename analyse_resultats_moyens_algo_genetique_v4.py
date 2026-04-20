import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from time import monotonic
from collections import deque
from math import exp

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

lAO = [float("inf"), 100, 1000, 10000]

lFichiers = ["lScores_GA_NN.txt", "lNbCoups_GA_NN.txt", "lDicoReseau_GA_NN.txt"]
with open(lFichiers[0], "r") as fichier:
    lScores = eval(fichier.read())
    iMax = max(i if score is not None else 0 for i, score in enumerate(lScores))
    assert iMax >= 0
    lScoresIndividus = list(map(list, zip(*lScores[:iMax+1])))

with open(lFichiers[1], "r") as fichier:
    lNbCoups = eval(fichier.read())
    iMax = max(i if nbCoups is not None else 0 for i,nbCoups in enumerate(lNbCoups))
    lNbCoupsIndividus = list(map(list, zip(*lNbCoups[:iMax+1])))

lGenerations = list(range(0, iMax+1))

fig,(axe1,axe2) = plt.subplots(2, 1)
axe1.set_position([0.1, 0.6, 0.7, 0.35])
axe2.set_position([0.1, 0.1, 0.7, 0.35])

animation = int(input("Animations ? (0 ou 1) : "))

def animer(fig, lCourbes, listeLValeurs, lGenerations):
    def update(frame):
        u = frame/nbFrames
        if True:
            u = u**3 * (u * (u*6 - 15) + 10) #u**2 * (3-2*u)
        t = u * (nbX-1) #[0 ; n-1] 
        i = int(t)
        dx = t-i
        for courbe, lValeurs in zip(lCourbes, listeLValeurs):
            lX = lGenerations[:i+1]
            lY = lValeurs[:i+1]
            if i+1 < nbX:
                lX.append(lGenerations[i] + dx*(lGenerations[i+1]-lGenerations[i]))
                lY.append(lValeurs[i] + dx*(lValeurs[i+1]-lValeurs[i]))
            courbe.set_data(lX, lY)
            #courbe.set_alpha(0.3 + 0.7*i/nbX)
        return lCourbes
    nbX = len(lGenerations)
    nbFrames = 10*nbX
    animation = FuncAnimation(fig, update, frames=nbFrames, init_func=None, fargs=None, save_count=None, interval=50, repeat_delay=1000, repeat=False, blit=True, cache_frame_data=False)
    return animation

lCourbesScores = [None]*len(lScoresIndividus)
for i, lScores in enumerate(lScoresIndividus):
    c = (i+1) / len(lScoresIndividus)
    titre = "lScoresMax" if i==0 else "lScoresMin" if i==len(lScoresIndividus)-1 else ""
    epaisseur = 4 if titre else 0.7
    if animation:
        lCourbesScores[i], = axe1.plot([], [], label=titre, color=(c, 1-c, (2*c)%1), linewidth=epaisseur)
    else :
        axe1.plot(lGenerations, lScores, label=titre, color=(c, 1-c, (2*c)%1), linewidth=epaisseur)
axe1.set_xlim(0, len(lGenerations)-1)
axe1.set_ylim(0, max(map(max, lScoresIndividus)))
if animation:
    animationAxe1 = animer(fig, lCourbesScores, lScoresIndividus, lGenerations)
axe1.legend(loc="center left", bbox_to_anchor=(1, 0.5))
axe1.set_xlabel("Génération")
axe1.set_ylabel("Score")

lCourbesNbCoups = [None]*len(lNbCoupsIndividus)
for i, lNbCoups in enumerate(lNbCoupsIndividus):
    c = (i+1) / len(lNbCoupsIndividus)
    titre = "lNbCoupsMax" if i==0 else "lNbCoupsMin" if i==len(lNbCoupsIndividus)-1 else ""
    epaisseur = 4 if titre else 0.7
    if animation:
        lCourbesNbCoups[i], = axe2.plot([], [], label=titre, color=(c, 1-c, (2*c)%1), linewidth=epaisseur)
    else :
        axe2.plot(lGenerations, lNbCoups, label=titre, color=(c, 1-c, (2*c)%1), linewidth=epaisseur)
axe2.set_xlim(0, len(lGenerations)-1)
axe2.set_ylim(0, max(map(max, lNbCoupsIndividus)))
if animation:
    animationAxe2 = animer(fig, lCourbesNbCoups, lNbCoupsIndividus, lGenerations)
axe2.legend(loc="center left", bbox_to_anchor=(1, 0.5))
axe2.set_xlabel("Génération")
axe2.set_ylabel("Nombre Coups")

plt.show()