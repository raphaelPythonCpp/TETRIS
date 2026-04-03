from random import uniform, shuffle, randint
from math import floor, ceil
from datetime import datetime
from TETRIS_TETROMINO_v3 import*

class Algorithme_Genetique(object):
    def __init__(self, jeu, algo, nbIndividus, nbGenerations, nbParties, nbConstantes, tauxSurvivant, nbLignes, nbColonnes, nbCoupsMax):
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
        
        self.modeCoups = 3
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
        self.nbIndividus = nbIndividus
        self.nbIndividusSurvivants = floor(self.nbIndividus * self.tauxSurvivant)
        self.nbIndividusAModifier = ceil((self.nbIndividus - self.nbIndividusSurvivants) / self.nbIndividusSurvivants)
        self.lIndividus = []
        for i in range(self.nbIndividus):
            self.lIndividus.append(Individu(jeu, self, algo, self.generer_combinaison(self.nbConstantes, vMin=-1, vMax=1), nbLignes, nbColonnes))

    def reset(self):
        pass
    
    def entrainement(self):
        tAvant = datetime.now()
        visuel = False
        sauvegardeFichiers = True
        lScoresMoyens = [(None,None) for iG in range(self.nbGenerations)]
        lNbCoupsMoyens = [(None, None) for iG in range(self.nbGenerations)]
        lConstantesMoyennes = [[None]*self.nbConstantes for iG in range(self.nbGenerations)]
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
            lRes.sort(key=lambda res : (res[1], res[2]), reverse=True)
            self.lIndividus = [self.lIndividus[iI] for iI, _, _ in lRes]
            print('\n',*[(round(scoreM/self.nbParties), round(nbCoupsM/self.nbParties)) for iI, scoreM, nbCoupsM in lRes])
            lScoresMoyens[iG] = (round(lRes[0][1]/self.nbParties), round(lRes[-1][1]/self.nbParties))
            lNbCoupsMoyens[iG] = (round(lRes[0][2]/self.nbParties), round(lRes[-1][2]/self.nbParties))
            lConstantesMoyennes[iG] = [round(constante, 2) for constante in self.lIndividus[0].lConstantes]
            iIndividuAM = self.nbIndividusSurvivants
            for iS in range(self.nbIndividusSurvivants):
                lConstantesS1 = self.lIndividus[iS].lConstantes
                self.lIndividus[iS].reset(lConstantesS1)
                lConstantesS2 = self.lIndividus[(iS+randint(0, self.nbIndividusSurvivants))%self.nbIndividusSurvivants].lConstantes
                for _ in range(self.nbIndividusAModifier):
                    if iIndividuAM < self.nbIndividus:
                        self.lIndividus[iIndividuAM].reset(self.generer_combinaison_variante_crossover(lConstantesS1, lConstantesS2, ecartMax=self.tauxMutation, vMin=-1, vMax=1))
                        iIndividuAM += 1
            self.tauxMutation *= self.decrementationTM
            #print(f"Sélection naturelle pour les {iIndividuAM} / {self.nbIndividus}")
            if sauvegardeFichiers:
                with open("lScoresMoyens.txt", "w") as fichier:
                    fichier.write(str(lScoresMoyens))
                with open("lNbCoupsMoyens.txt", "w") as fichier:
                    fichier.write(str(lNbCoupsMoyens))
                with open("lConstantesMoyennes.txt", "w") as fichier:
                    fichier.write(str(lConstantesMoyennes))
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
            








class Individu(object):
    def __init__(self, jeu, algoGenetique, algo, lConstantes, nbLignes, nbColonnes):
        self.jeu = jeu
        self.algoGenetique = algoGenetique
        self.algo = algo
        self.nbCoups = 0
        
        self.lConstantes = lConstantes
        self.nbConstantes = len(self.lConstantes)
        self.score = 0
        self.finJeu = False
        #Grille
        self.nbLignes, self.nbColonnes = nbLignes, nbColonnes
        self.grille = [[None]*self.nbColonnes for _ in range(self.nbLignes)]
        #Pieces
        self.lPositionsPieces = []
        self.piece = None
        self.holdPiece = None
        self.reset(self.lConstantes)

    def reset(self, lConstantes):
        self.lConstantes = lConstantes
        self.nbConstantes = len(self.lConstantes)
        self.nbCoups = 0
        self.score = 0
        self.finJeu = False
        self.grille = [[None]*self.nbColonnes for _ in range(self.nbLignes)]
        self.lPositionsPieces = []
        self.holdPiece = None
        self.piece = None
        self.generer_piece()

    def generer_piece(self):
        if self.algoGenetique.modeCoups == 3 and self.holdPiece is None : #au début
            self.holdPiece = Tetromino(self.jeu, self.algoGenetique.lProchainesPieces[self.nbCoups], entrainement=True)
            self.holdPiece.reset(self.grille)
        prochainType = self.algoGenetique.lProchainesPieces[self.nbCoups+1]
        if self.piece is None:
            self.piece = Tetromino(self.jeu, prochainType, entrainement=True)
        else :
            self.piece.type = prochainType
            self.piece.orientation = 0
            self.piece.matrice = self.jeu.dicoMatricesPieces[(prochainType, 0)]
            self.piece.couleur = self.jeu.dicoCouleursPieces[prochainType]
        if self.piece.reset(self.grille):
            self.finJeu = True

    def jouer(self):
        if self.finJeu:
            return
        if self.algoGenetique.modeCoups == 1 :
            self.lPositionsPieces = self.algo.calculer_toutes_positions_1_coup(self.grille, self.piece)
            self.algo.jouer_1_coup(self.grille, self.lPositionsPieces, self.piece, jeu=self, lConstantes=self.lConstantes, reel=False, fScore=self.changer_score)
        elif self.algoGenetique.modeCoups == 3:
            self.lPositionsPieces = [self.algo.calculer_toutes_positions_1_coup(self.grille, self.piece), self.algo.calculer_toutes_positions_1_coup(self.grille, self.holdPiece)]
            self.algo.joueur_3_coups(self.grille, self.lPositionsPieces, self.piece, self.holdPiece, jeu=self, lConstantes=self.lConstantes, reel=False, fScore=self.changer_score)
        self.nbCoups += 1
        self.score += 5
        if self.finJeu :
            return
        self.generer_piece()

    def changer_score(self, gain):
        self.score += gain

    def mettre_piece_hold(self):
        if self.holdPiece is None:
            self.holdPiece = self.piece
            self.generer_piece()
        else :
            self.holdPiece, self.piece = self.piece, self.holdPiece
            if self.piece.reset(self.grille):
                self.finJeu = True