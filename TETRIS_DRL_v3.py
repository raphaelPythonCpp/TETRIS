import torch
from datetime import datetime
from math import exp, log, ceil
from random import uniform, randint, shuffle, sample
from collections import deque
from copy import deepcopy
from TETRIS_INDIVIDU_NN_v1 import*

class Policy_Gradient(torch.nn.Module):
    def __init__(self, jeu, algo, nbEpisodes, nbParties, nbCoupsMax, modeCoups, nbConstantes, nbLignes, nbColonnes):
        super().__init__()
        self.jeu = jeu
        self.algo = algo
        #Entrainement
        self.nbConstantes = nbConstantes
        self.nbEpisodes = nbEpisodes
        self.nbParties = nbParties
        self.nbCoupsMax = nbCoupsMax
        self.modeCoups = modeCoups
        self.nbLignes, self.nbColonnes = nbLignes, nbColonnes
        #Constantes entrainement
        self.gamma = 0.999
        #Réseau neuronnes
        lCouches = [self.nbConstantes, 1]
                  #[self.nbConstantes, 8, 1)]
                  #[self.nbConstantes, 16, 1)]
                  #[self.nbConstantes, 32, 16, 1]
        #A FINIR !
        #self.optimiseur = torch.optim.Adam(self.modele.parameters(), lr=1e-3)
        self.fonctionLoss = torch.nn.MSELoss()
        self.trajectoire = []

        #Jeu
        self.generer_pieces_partie()
        #self.individu = Individu_NN(self.jeu, self, self.algo, lNbNoeuds, None, self.nbLignes, self.nbColonnes)
        #A Finir

    def reset(self):
        pass

    def entrainement(self):
        tAvant = datetime.now()
        sauvegardeFichiers = True
        lScores = [None for iE in range(self.nbEpisodes)]
        lNbCoups = [None for iE in range(self.nbEpisodes)]
        lConstantes = [None for iE in range(self.nbEpisodes)]
        for iE in range(self.nbEpisodes):
            self.trajectoire = []
            sommeScores, sommeNbCoups = 0, 0
            for iP in range(self.nbParties):
                print('\r' + ' '*120 + f"\rEntrainement DQL : Episode {iE+1} ({(iE+1)/self.nbEpisodes*100:.2f}%) || Partie {iP+1} ({(iP+1)/self.nbParties*100:.2f}%) || ScoreAvant : {lScores[iE-1] if lScores[iE-1] is not None else -1:.2f} || nbCoupsAvant : {lNbCoups[iE-1] if lNbCoups[iE-1] is not None else -1:.2f}", end="", flush=True)                
                self.generer_pieces_partie()
                self.individu.reset()
                while not self.individu.finJeu and self.individu.nbCoups < self.nbCoupsMax:
                    #Choisir Position
                    self.individu.calculer_toutes_positions()
                    lPositions1 = self.individu.lPositionsPieces
                    if not lPositions1:
                        self.individu.finJeu = True
                        break
                    lCaracteristiques = [self.algo.caracteristiques(self.individu.grille, *position, in_place=True)[0] for position in lPositions1]
                    listeInput = torch.tensor(lCaracteristiques, dtype=torch.float32)
                    lOutput = self.modele(listeInput).squeeze(-1)
                    lProbas = torch.softmax(lOutput, dim=0)
                    iP1 = torch.multinomial(lProbas, 1).item()
                    logProbas = torch.log(lProbas[iP1]+1e-10)
                    #Jouer
                    lCaracteristiques1 = lCaracteristiques[iP1]
                    self.individu.appliquer_position(lPositions1[iP1])
                    self.individu.jouer(False, False)
                    recompense = self.recompense(lCaracteristiques1+[self.individu.finJeu])
                    self.trajectoire.append((logProbas, recompense))
                sommeScores += self.individu.score
                sommeNbCoups += self.individu.nbCoups

            if not self.trajectoire:
                continue
            G = 0
            lG = []
            for i, (_, recompense) in enumerate(reversed(self.trajectoire)):
                G = recompense + self.gamma * G
                lG.append(G)
            lG.reverse()
            lG = torch.tensor(lG, dtype=torch.float32)
            lG = (lG - lG.mean()) / (lG.std() + 1e-8) if lG.std() > 1e-8 else lG
            loss = 0
            for (logProbas,_), G in zip(self.trajectoire, lG):
                loss -= logProbas * G
            entropie = -(lProbas * torch.log(lProbas + 1e-10)).sum()
            loss -= 0.01 * entropie
            #Back prop
            self.optimiseur.zero_grad()
            loss.backward()
            self.optimiseur.step()
                
            lScores[iE] = sommeScores / self.nbParties
            lNbCoups[iE] = sommeNbCoups / self.nbParties
            lConstantes[iE] = {k: v.detach().cpu().numpy().tolist() for k, v in self.modele.state_dict().items()}
            if sauvegardeFichiers:
                with open("lScores_DRL.txt", "w") as fichier:
                    fichier.write(str(lScores))
                with open("lNbCoups_DRL.txt", "w") as fichier:
                    fichier.write(str(lNbCoups))
                if iE%100 == 0:
                    with open("lConstantes_DRL.txt", "w") as fichier:
                        fichier.write(str(lConstantes))

        lConstantesFinales = {k: v.detach().cpu().numpy().tolist() for k, v in self.modele.state_dict().items()}
        print('\n',lConstantesFinales)
        self.algo.lConstantes = lConstantesFinales
        t = datetime.now()
        print(f"{tAvant.hour}:{tAvant.minute}'{tAvant.second}\" -> {t.hour}:{t.minute}'{t.second}\"")

    def recompense(self, lCaracteristiques):
        hMaxG, hMaxP, sumHG, nbTN, I, nbL, sommePuits, fin = lCaracteristiques
        recompense = 1
        recompense -= hMaxG * 0.5
        #recompense -= hMaxP * 0.1
        recompense -= nbTN * 2
        #recompense -= I * 0.1
        recompense += (nbL * 4)**2
        recompense -= sommePuits * 2
        recompense -= 100 if fin else 0
        return recompense
    
    def generer_pieces_partie(self):
        self.lProchainesPieces = []
        for i in range(ceil((self.nbCoupsMax+2)/len(self.jeu.lTypePieces))):
            l = self.jeu.lTypePieces.copy()
            shuffle(l)
            self.lProchainesPieces.extend(l)

"""
L= -logπ(a|s)⋅G
∇J=E[∇logπ(a|s)⋅(G-b)]
"""