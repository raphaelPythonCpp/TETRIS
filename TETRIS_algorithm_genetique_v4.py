from random import uniform, shuffle, randint
from math import floor, ceil
from datetime import datetime
from TETRIS_TETROMINO_v3 import*
from TETRIS_INDIVIDU_v1 import*

class Algorithme_Genetique(object):
    def __init__(self, jeu, algo, nbIndividus, nbGenerations, nbParties, nbConstantes, tauxSurvivant, tauxRandom, nbLignes, nbColonnes, nbCoupsMax, modeCoups):
        self.jeu = jeu
        self.algo = algo
        
        self.nbGenerations = nbGenerations
        self.nbParties = nbParties
        self.nbConstantes = nbConstantes

        self.nbLignes = nbLignes
        self.nbColonnes = nbColonnes
        
        self.tauxMutationInit = 1
        self.tauxMutation = self.tauxMutationInit
        self.decrementationTM = (0.01 / self.tauxMutation) ** (1/self.nbGenerations)
        
        self.modeCoups = modeCoups
        self.nbCoupsMax = nbCoupsMax
        #lProchainesPieces
        self.tauxPartiesRandom = 0.25
        self.nbPartiesMemes = floor(self.nbParties * (1 - self.tauxPartiesRandom))
        self.nbPartiesRandom = self.nbParties - self.nbPartiesMemes
        self.listeLProchainesPieces = []
        for iP in range(self.nbPartiesMemes):
            self.listeLProchainesPieces.append(self.generer_pieces_partie())
        self.lProchainesPieces = self.listeLProchainesPieces[0]
        #Individus
        self.tauxSurvivant = tauxSurvivant #en pour 1 (ex : 0.2)
        self.tauxRandom = tauxRandom
        self.nbIndividus = nbIndividus
        self.nbIndividusSurvivants = floor(self.nbIndividus * self.tauxSurvivant)
        self.nbIndividusRandom = floor(self.nbIndividus * self.tauxRandom)
        self.nbIndividusAModifier = ceil((self.nbIndividus - (self.nbIndividusSurvivants+self.nbIndividusRandom)) / self.nbIndividusSurvivants)
        self.lIndividus = []
        for i in range(self.nbIndividus):
            self.lIndividus.append(Individu(jeu, self, algo, self.generer_combinaison(self.nbConstantes, vMin=-1, vMax=1), nbLignes, nbColonnes))

    def reset(self):
        pass
    
    def entrainement(self):
        tAvant = datetime.now()
        visuel = False
        sauvegardeFichiers = True
        lScores = [(None,None) for iG in range(self.nbGenerations)]
        lNbCoups = [(None, None) for iG in range(self.nbGenerations)]
        lConstantes = [[None]*self.nbConstantes for iG in range(self.nbGenerations)]
        for iG in range(self.nbGenerations):
            lRes = [[iI,0,0] for iI in range(self.nbIndividus)]
            for iP in range(self.nbParties):
                print('\r' + ' '*100 + f"\rEntrainement Algorithme Génétique : Génération {iG+1} ({(iG+1)/self.nbGenerations*100:.2f}%) || Partie {iP+1} ({(iP+1)/self.nbParties*100:.2f}%)", end="", flush=True)                
                nbIndividusRestants = self.nbIndividus
                self.lProchainesPieces = self.listeLProchainesPieces[iP] if iP < self.nbPartiesMemes else self.generer_pieces_partie()
                for individu in self.lIndividus:
                    individu.reset(individu.lConstantes)
                nbCoups = 0
                while nbIndividusRestants > 0 and nbCoups < self.nbCoupsMax:
                    nbCoups += 1
                    for individu in self.lIndividus:
                        if individu.finJeu :
                            continue
                        individu.jouer()
                        """if individu.finJeu : #mort
                            nbIndividusRestants -= 1"""
                        if visuel :
                            self.jeu.fenetre.fill((0,0,0))
                            self.jeu.afficher_grille(individu.grille, self.jeu.tailleCase, self.jeu.xDebutCases, self.jeu.yDebutCases, piece=individu.piece, ombre=False, coin=False)
                            self.jeu.fenetre.blit(self.jeu.police.render(f"Score : {individu.score}", False, self.jeu.couleurTextes), (0, 0))
                            pygame.display.flip()
                            pygame.time.delay(100)
                    nbIndividusRestants = sum(not individu.finJeu for individu in self.lIndividus)
                for iI, individu in enumerate(self.lIndividus):
                    lRes[iI][1] += individu.score
                    lRes[iI][2] += individu.nbCoups
            #Sélection naturelle + mutations
            lRes.sort(key=lambda res : (res[1] + 5*res[2]), reverse=True)
            sommeScoresMoyens = sum(lRes[i][1] for i in range(self.nbIndividus-self.nbIndividusRandom))/(self.nbIndividus-self.nbIndividusRandom)
            sommeNbCoupsMoyens = sum(lRes[i][2] for i in range(self.nbIndividus-self.nbIndividusRandom))/(self.nbIndividus-self.nbIndividusRandom)
            self.lIndividus = [self.lIndividus[iI] for iI, _, _ in lRes]
            print('\n',*[(round(scoreM/self.nbParties), round(nbCoupsM/self.nbParties)) for iI, scoreM, nbCoupsM in lRes])
            lScores[iG] = (round(lRes[0][1]/self.nbParties), round(sommeScoresMoyens/self.nbParties))
            lNbCoups[iG] = (round(lRes[0][2]/self.nbParties), round(sommeNbCoupsMoyens/self.nbParties))
            lConstantes[iG] = [round(constante, 2) for constante in self.lIndividus[0].lConstantes]
            iIndividuAM = self.nbIndividusSurvivants
            for iS in range(self.nbIndividusSurvivants):
                lConstantesS1 = self.lIndividus[iS].lConstantes
                self.lIndividus[iS].reset(lConstantesS1)
                lConstantesS2 = self.lIndividus[(iS+randint(0, self.nbIndividusSurvivants-1))%self.nbIndividusSurvivants].lConstantes
                for _ in range(self.nbIndividusAModifier):
                    if iIndividuAM < self.nbIndividus:
                        self.lIndividus[iIndividuAM].reset(self.generer_combinaison_variante_crossover(lConstantesS1, lConstantesS2, ecartMax=self.tauxMutation, vMin=-1, vMax=1))
                        iIndividuAM += 1
            for iR in range(self.nbIndividusRandom):
                self.lIndividus[-(iR+1)].reset(self.generer_combinaison(self.nbConstantes, vMin=-1, vMax=1))
            self.tauxMutation *= self.decrementationTM
            #print(f"Sélection naturelle pour les {iIndividuAM} / {self.nbIndividus}")
            if sauvegardeFichiers:
                with open("lScores.txt", "w") as fichier:
                    fichier.write(str(lScores))
                with open("lNbCoups.txt", "w") as fichier:
                    fichier.write(str(lNbCoups))
                with open("lConstantes.txt", "w") as fichier:
                    fichier.write(str(lConstantes))
        lConstantesFinales = [round(constante, 2) for constante in self.lIndividus[0].lConstantes]
        print(lConstantesFinales)
        self.algo.lConstantes = lConstantesFinales
        t = datetime.now()
        print(f"{tAvant.hour}:{tAvant.minute}'{tAvant.second}\" -> {t.hour}:{t.minute}'{t.second}\"")

    def generer_pieces_partie(self):
        lProchainesPieces = []
        for i in range(ceil((self.nbCoupsMax+2)/len(self.jeu.lTypePieces))):
            l = self.jeu.lTypePieces.copy()
            shuffle(l)
            lProchainesPieces.extend(l)
        return lProchainesPieces

    def generer_combinaison(self, nbConstantes, vMin, vMax):
        lConstantes = [uniform(vMin, vMax) for _ in range(nbConstantes)]
        return lConstantes
    
    def generer_combinaison_variante(self, lConstantes, ecartMax, vMin, vMax):
        lConstantes2 = [max(vMin, min(vMax, lConstantes[i]+uniform(-ecartMax, +ecartMax))) for i in range(len(lConstantes))]
        return lConstantes2
    
    def generer_combinaison_variante_crossover(self, lConstantes1, lConstantes2, ecartMax, vMin, vMax):
        lConstantes = [None]*len(lConstantes1)
        for i in range(len(lConstantes1)):
            constante = lConstantes1[i] if uniform(0,1) <= 0.5 else lConstantes2[i]
            lConstantes[i] = max(vMin, min(vMax, constante+uniform(-ecartMax, +ecartMax)))
        return lConstantes