import matplotlib.pyplot as plt

GA = False
NES = True

if GA :
    lFichiers = ["lScoresMoyens.txt", "lNbCoupsMoyens.txt", "lConstantesMoyennes.txt"]
elif NES :
    lFichiers = ["lScoresMoyensTotal_NES.txt", "lNbCoupsMoyensTotal_NES.txt", "lLMeilleursConstantesTotal_NES.txt"]

with open(lFichiers[0], "r") as fichier:
    lScoresMoyens = eval(fichier.read())
    lScoresMax = [scoreMoyen[0] for scoreMoyen in lScoresMoyens]
    lScoresMin = [scoreMoyen[1] for scoreMoyen in lScoresMoyens]
with open(lFichiers[1], "r") as fichier:
    lNbCoupsMoyens = eval(fichier.read())
    lNbCoupsMax = [nbCoupsMoyen[0] for nbCoupsMoyen in lNbCoupsMoyens]
    lNbCoupsMin = [nbCoupsMoyen[1] for nbCoupsMoyen in lNbCoupsMoyens]
with open(lFichiers[2], "r") as fichier:
    lConstantesMoyennes = eval(fichier.read())
    lConstantes = [[combinaison[i] for combinaison in lConstantesMoyennes] for i in range(len(lConstantesMoyennes[0]))]
    lNomsConstantes = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta"]

fig,(axe1,axe2,axe3) = plt.subplots(3, 1)
axe1.set_position([0.1, 0.7, 0.7, 0.2])
axe2.set_position([0.1, 0.4, 0.7, 0.2])
axe3.set_position([0.1, 0.1, 0.7, 0.2])

lGenerations = list(range(1, len(lScoresMoyens)+1))
axe1.plot(lGenerations, lScoresMax, label="lScoresMax", color=(0,0.8,0))
axe1.plot(lGenerations, lScoresMin, label="lScoresMin", color=(0.8,0,0))
axe1.legend(loc="center left", bbox_to_anchor=(1, 0.5))

axe2.plot(lGenerations, lNbCoupsMax, label="lNbCoupsMax", color=(0,0.8,0))
axe2.plot(lGenerations, lNbCoupsMin, label="lNbCoupsMin", color=(0.8,0,0))
axe2.legend(loc="center left", bbox_to_anchor=(1, 0.5))

for i in range(len(lConstantes)):
    c = i/len(lConstantes)
    axe3.plot(lGenerations, lConstantes[i], label=lNomsConstantes[i], color=(c, 1-c, (2*c)%1))
axe3.legend(loc="center left", bbox_to_anchor=(1, 0.5))
axe3.set_ylim(-1.1, 1.1)

plt.show()