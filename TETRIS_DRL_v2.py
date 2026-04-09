import torch
from datetime import datetime
from math import exp, log, ceil
from random import uniform, randint, shuffle, sample
from collections import deque
from copy import deepcopy
from TETRIS_INDIVIDU_v1 import*

class DQL(torch.nn.Module):
    def __init__(self, jeu, algo, nbEpisodes, nbCoupsMax, modeCoups, nbConstantes, nbLignes, nbColonnes):
        super().__init__()
        self.jeu = jeu
        self.algo = algo
        #Entrainement
        self.nbConstantes = nbConstantes
        self.nbEpisodes = nbEpisodes
        self.nbCoupsMax = nbCoupsMax
        self.modeCoups = modeCoups
        self.nbLignes, self.nbColonnes = nbLignes, nbColonnes
        #Constantes entrainement
        self.epsilon = 1 #randomness
        self.espilonDecay = exp(log(0.05/self.epsilon) / self.nbEpisodes)
        self.gamma = 0.99
        #Jeu
        self.generer_pieces_partie()
        self.individu = Individu(self.jeu, self, self.algo, None, self.nbLignes, self.nbColonnes)
        #Réseau neuronnes
        self.modele = torch.nn.Sequential(#torch.nn.Linear(self.nbConstantes, 1, False))
                                          #torch.nn.Linear(self.nbConstantes, 8, True), torch.nn.ReLU(), torch.nn.Linear(8, 1, True))
                                          torch.nn.Linear(self.nbConstantes, 16, True), torch.nn.ReLU(), torch.nn.Linear(16, 1, True))
                                          #torch.nn.Linear(self.nbConstantes,32,True), torch.nn.ReLU(), torch.nn.Linear(32,16,True), torch.nn.ReLU(), torch.nn.Linear(16,1,True))
        self.modeleCible = deepcopy(self.modele)
        self.modeleCible.load_state_dict(self.modele.state_dict())
        self.nbMAJModeleCible = self.nbEpisodes // 20
        self.optimiseur = torch.optim.Adam(self.modele.parameters(), lr=1e-3)
        self.fonctionLoss = torch.nn.MSELoss()
        self.replayBuffer = deque(maxlen=10000)
        self.tailleBatch = 32

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
            self.generer_pieces_partie()
            self.individu.reset()
            while not self.individu.finJeu and self.individu.nbCoups < self.nbCoupsMax:
                #Choisir Position
                self.individu.calculer_toutes_positions()
                lPositions1 = self.individu.lPositionsPieces
                if not lPositions1:
                    self.individu.finJeu = True
                    break
                if uniform(0,1) < self.epsilon:
                    iP1 = randint(0, len(lPositions1)-1)
                else:
                    listeLX = torch.tensor([self.algo.caracteristiques(self.individu.grille, *position)[0] for position in lPositions1], dtype=torch.float32)
                    with torch.no_grad():
                        lQValue = self.modele(listeLX).squeeze(-1)
                    iP1 = torch.argmax(lQValue).item()
                #Jouer
                lCaracteristiques1,_ = self.algo.caracteristiques(self.individu.grille, *lPositions1[iP1])
                lX = torch.tensor(lCaracteristiques1, dtype=torch.float32)
                self.individu.appliquer_position(lPositions1[iP1])
                self.individu.jouer(False, False)
                recompense = self.recompense(lCaracteristiques1+[self.individu.finJeu])
                
                #Calculer Recompense
                self.individu.calculer_toutes_positions()
                lPositions2 = self.individu.lPositionsPieces
                if not lPositions2:
                    self.individu.finJeu = True
                    self.replayBuffer.append((lCaracteristiques1, lPositions1[iP1], -100, lCaracteristiques1, True))
                    break
                scoreMax2 = -float("inf")
                iP2 = 0
                for i, position in enumerate(lPositions2):
                    lCaracteristiques,_ = self.algo.caracteristiques(self.individu.grille, *position)
                    lX = torch.tensor(lCaracteristiques, dtype=torch.float32)
                    with torch.no_grad():
                        score = self.modele(lX).item()
                    if score > scoreMax2:
                        scoreMax2 = score
                        iP2 = i
                lCaracteristiques2,_ = self.algo.caracteristiques(self.individu.grille, *lPositions2[iP2])
                self.replayBuffer.append((lCaracteristiques1, lPositions1[iP1], recompense, lCaracteristiques2, self.individu.finJeu))
                
                #BackProp   
                if len(self.replayBuffer) >= self.tailleBatch:
                    batch = sample(self.replayBuffer, self.tailleBatch)
                    listeLCar1, lPositions, lRecompenses, listeLCar2, lFin = zip(*batch)

                    listeLCar1 = torch.tensor(listeLCar1, dtype=torch.float32)
                    lRecompenses = torch.tensor(lRecompenses, dtype=torch.float32)
                    listeLCar2 = torch.tensor(listeLCar2, dtype=torch.float32)
                    lFin = torch.tensor(lFin, dtype=torch.float32)

                    lQValue = self.modele(listeLCar1).squeeze(-1)
                    with torch.no_grad():
                        qNextValue = self.modeleCible(listeLCar2).squeeze(-1)
                        lCibles = lRecompenses + self.gamma * qNextValue * (1 - lFin)
                    loss = self.fonctionLoss(lQValue, lCibles)
                    self.optimiseur.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.modele.parameters(), 1.0)
                    self.optimiseur.step()

            lScores[iE] = self.individu.score
            lNbCoups[iE] = self.individu.nbCoups
            lConstantes[iE] = {k: v.clone() for k, v in self.modele.state_dict().items()}
            if sauvegardeFichiers:
                with open("lScores_DRL.txt", "w") as fichier:
                    fichier.write(str(lScores))
                with open("lNbCoups_DRL.txt", "w") as fichier:
                    fichier.write(str(lNbCoups))
                if iE%100 == 0:
                    with open("lConstantes_DRL.txt", "w") as fichier:
                        fichier.write(str(lConstantes))
            self.epsilon *= self.espilonDecay
            if iE % self.nbMAJModeleCible == 0:
                self.modeleCible.load_state_dict(self.modele.state_dict())
        lConstantesFinales = {k: v.clone() for k, v in self.modele.state_dict().items()}
        print('\n',lConstantesFinales)
        self.algo.lConstantes = lConstantesFinales
        t = datetime.now()
        print(f"{tAvant.hour}:{tAvant.minute}'{tAvant.second}\" -> {t.hour}:{t.minute}'{t.second}\"")

    def recompense(self, lCaracteristiques):
        hMaxG, hMaxP, sumHG, nbTN, I, nbL, sommePuits, fin = lCaracteristiques
        recompense = 1
        recompense -= hMaxG * 0.2
        #recompense -= hMaxP * 0.1
        recompense -= nbTN * 0.5
        #recompense -= I * 0.1
        recompense += nbL * 10
        recompense -= sommePuits * 0.3
        recompense -= 100 if fin else 0
        return recompense
    
    def generer_pieces_partie(self):
        self.lProchainesPieces = []
        for i in range(ceil((self.nbCoupsMax+2)/len(self.jeu.lTypePieces))):
            l = self.jeu.lTypePieces.copy()
            shuffle(l)
            self.lProchainesPieces.extend(l)

"""
état (state) → action → récompense → nouvel état

state = env.reset()
for step in range(max_steps):

    if random.random() < epsilon:
        action = random.randrange(n_actions)
    else:
        action = modele(state).argmax().item()

    next_state, reward, done, _ = env.step(action)

    replay_buffer.push(state, action, reward, next_state, done)

    state = next_state

    if len(replay_buffer) >= batch_size:
        train_step()

    backprop
"""