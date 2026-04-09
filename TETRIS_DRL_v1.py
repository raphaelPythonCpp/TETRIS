import torch
from datetime import datetime
from TETRIS_INDIVIDU_v1 import*
from math import exp, log, ceil
from random import uniform, randint, shuffle

class DQL(torch.nn.Module):
    def __init__(self, jeu, algo, nbEpisodes, nbCoupsMax, modeCoups, nbConstantes, nbLignes, nbColonnes):
        super().__init__()
        self.jeu = jeu
        self.algo = algo
        #Entrainement
        self.nbConstantes = nbConstantes
        self.nbEpisodes = nbEpisodes
        self.nbCoupsMax = nbCoupsMax
        self.modeCoups = 1 #modeCoups
        self.nbLignes, self.nbColonnes = nbLignes, nbColonnes
        #Constantes entrainement
        self.epsilon = 1 #randomness
        self.espilonDecay = exp(log(0.01/self.epsilon) / self.nbEpisodes)
        self.gamma = 0.95
        #Jeu
        self.generer_pieces_partie()
        self.individu = Individu(self.jeu, self, self.algo, None, self.nbLignes, self.nbColonnes)
        #Réseau neuronnes
        self.modele = torch.nn.Sequential(torch.nn.Linear(self.nbConstantes,32,True), torch.nn.ReLU(), torch.nn.Linear(32,16,True), torch.nn.ReLU(), torch.nn.Linear(16,1,True))
        self.optimiseur = torch.optim.Adam(self.modele.parameters(), lr=1e-3)
        self.fonctionLoss = torch.nn.MSELoss()

    def reset(self):
        pass

    def entrainement(self):
        tAvant = datetime.now()
        sauvegardeFichiers = True
        lScores = [None for iE in range(self.nbEpisodes)]
        lNbCoups = [None for iE in range(self.nbEpisodes)]
        lConstantes = [None for iE in range(self.nbEpisodes)]
        for iE in range(self.nbEpisodes):
            print('\r' + ' '*100 + f"\rEntrainement DQL : Episode {iE+1} ({(iE+1)/self.nbEpisodes*100:.2f}%) || ScoreAvant : {lScores[iE-1] if lScores[iE-1] is not None else -1:.2f} || nbCoupsAvant : {lNbCoups[iE-1] if lNbCoups[iE-1] is not None else -1:.2f}", end="", flush=True)                
            self.individu.reset()
            while not self.individu.finJeu :
                self.individu.calculer_toutes_positions()
                if not self.individu.lPositionsPieces:
                    self.individu.finJeu = True
                    break
                if uniform(0,1) < self.epsilon:
                    iP = randint(0, len(self.individu.lPositionsPieces)-1)
                else:
                    scoreMax = -float("inf")
                    iP = 0
                    for i, position in enumerate(self.individu.lPositionsPieces):
                        lCaracteristiques,_ = self.algo.caracteristiques(self.individu.grille, *position)
                        lX = torch.tensor(lCaracteristiques, dtype=torch.float32)
                        with torch.no_grad():
                            score = self.modele(lX).item()
                        if score > scoreMax:
                            scoreMax = score
                            iP = i
                lCaracteristiques,_ = self.algo.caracteristiques(self.individu.grille, *self.individu.lPositionsPieces[iP])
                lX = torch.tensor(lCaracteristiques, dtype=torch.float32)
                scorePredi = self.modele(lX)
                self.individu.appliquer_position(self.individu.lPositionsPieces[iP])
                self.individu.jouer(False, False)
                recompense = self.recompense(lCaracteristiques+[self.individu.finJeu])
                prochaineGrille = self.individu.grille
                with torch.no_grad():
                    lProchainsScores = []
                    self.individu.calculer_toutes_positions()
                    if not self.individu.lPositionsPieces:
                        self.individu.finJeu = True
                        break
                    for prochainPosition in self.individu.lPositionsPieces:
                        lCaracteristiques,_ = self.algo.caracteristiques(prochaineGrille, *prochainPosition)
                        lX = torch.tensor(lCaracteristiques, dtype=torch.float32)
                        lProchainsScores.append(self.modele(lX))
                    prochainScoreMax = torch.max(torch.stack(lProchainsScores)) if lProchainsScores else torch.tensor(0.0)
                scoreObjectif = torch.tensor(recompense, dtype=torch.float32) + self.gamma * prochainScoreMax.detach()
                #BackProp   
                loss = self.fonctionLoss(scorePredi, scoreObjectif)
                self.optimiseur.zero_grad()
                loss.backward()
                self.optimiseur.step() 

            lScores[iE] = self.individu.score
            lNbCoups[iE] = self.individu.nbCoups
            lConstantes[iE] = [p.detach().cpu().numpy().tolist() for p in self.modele.parameters()] #poids modèle
            if sauvegardeFichiers:
                with open("lScores_DRL.txt", "w") as fichier:
                    fichier.write(str(lScores))
                with open("lNbCoups_DRL.txt", "w") as fichier:
                    fichier.write(str(lNbCoups))
                with open("lConstantes_DRL.txt", "w") as fichier:
                    fichier.write(str(lConstantes))
            self.epsilon *= self.espilonDecay
        lConstantesFinales = [p.detach().cpu().numpy().tolist() for p in self.modele.parameters()]
        print(lConstantesFinales)
        self.algo.lConstantes = lConstantesFinales
        t = datetime.now()
        print(f"{tAvant.hour}:{tAvant.minute}'{tAvant.second}\" -> {t.hour}:{t.minute}'{t.second}\"")

    def recompense(self, lCaracteristiques):
        hMaxG, hMaxP, sumHG, nbTN, I, nbL, sommePuits, fin = lCaracteristiques
        recompense = 0
        #recompense -= hMaxG * 0.1
        #recompense -= hMaxP * 0.1
        #recompense -= nbTN * 0.5
        recompense += nbL * 10
        if fin:
            recompense = -100
        return recompense
    
    def generer_pieces_partie(self):
        self.lProchainesPieces = []
        for i in range(ceil((self.nbCoupsMax+2)/len(self.jeu.lTypePieces))):
            l = self.jeu.lTypePieces.copy()
            shuffle(l)
            self.lProchainesPieces.extend(l)

"""
état (state) → action → récompense → nouvel état
"""