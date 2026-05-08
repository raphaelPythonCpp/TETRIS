# Créé par raphael.garivier, le 24/02/2026 en Python 3.7
import pygame
import random as rd
from math import floor, ceil, sqrt
from datetime import datetime
from TETRIS_TETROMINO_v5 import*

class Jeu(object):
    def __init__(self, fenetre, lAttributsPolice, horloge, nbColonnes=5, nbLignes = 8, visuel=True, menus=True, nbFramesAffichage=1, lNbNoeuds=[7,1], algorithme=False, entrainementGreedy=False, entrainementGenetique=False, entrainementNES=False, entrainementDRL=False, gameInfini=False):
        self.horloge = horloge
        self.quitterProgramme = False
        self.finJeu = False
        self.visuel = visuel
        self.couleurTextes = (150,150,255)
        self.score = 0
        self.texteScore = None
        self.dicoScores = {0 : 0,
                           1 : 40,
                           2 : 100,
                           3 : 300,
                           4 : 1200}
        self.nbCoups = 0
        self.nbCoupsMax = None
        self.changer_game_nb_coups_max(gameInfini)
        self.texteNbCoups = None
        self.nbBlocs = 0
        self.sommeNbBlocs = 0
        self.calcul_sommeNbBlocs = False
        self.texteSommeNbBlocs = None
        #Graphiques
        self.fenetre = fenetre
        self.lAttributsPolice = lAttributsPolice
        nomPolice, taillePolice, grasPolice, italiquePolice = self.lAttributsPolice
        self.police = pygame.font.SysFont(nomPolice, taillePolice, bold=grasPolice, italic=italiquePolice)
        self.nbFramesAffichage = nbFramesAffichage
        self.iFrameAffichage = 0
        self.wF, self.hF = pygame.display.get_surface().get_size()
        self.bordure = 0.03
        self.couleurFond = (255,255,255)
        self.couleurFondGrille = tuple(255-cF for cF in self.couleurFond)
        self.couleurBorduresGrille = tuple(0.8*cFG+0.2*cF for cFG,cF in zip(self.couleurFondGrille, self.couleurFond))
        #Grille
        self.nbColonnes, self.nbLignes = nbColonnes, nbLignes
        self.lDicoModesGrille = [{"nbGrilles" : 1, "tailleCases" : self.hF / (1.5*self.nbLignes), "listeLOrientations" : [[0]]},
                                 {"nbGrilles" : 3, "tailleCases" : self.hF / (3.5*self.nbLignes), "listeLOrientations" : [[0,1,2], [3,0,1], [2,3,0]]},
                                 {"nbGrilles" : 4, "tailleCases" : self.hF / (3.5*self.nbLignes), "listeLOrientations" : [[0,1,2,3], [3,0,1,2], [2,3,0,1], [1,2,3,0]]}]
        self.lDicoModesGrille[0]["lXYDebut"] = [(self.wF/2 - nbColonnes/2 * self.lDicoModesGrille[0]["tailleCases"], self.hF/2 - nbLignes/2 * self.lDicoModesGrille[0]["tailleCases"])]
        ecart = self.lDicoModesGrille[1]["tailleCases"]*self.nbColonnes/2
        self.lDXY = [(0,1), (1,0), (0,-1), (-1,0)]
        lDXYEcart = [(ecart*dx, ecart*dy) for dx,dy in [(-1,1), (1, 1), (1, -1), (-1, -1)]]
        self.lDicoModesGrille[1]["lXYDebut"] = [(self.wF/2 + dx, self.hF/2 + dy) for dx,dy in lDXYEcart]
        self.lDicoModesGrille[2]["lXYDebut"] = self.lDicoModesGrille[1]["lXYDebut"].copy()
        self.modeGrille = 0 #0-2
        self.grille = [[None]*self.nbColonnes for _ in range(self.nbLignes)]
        self.grilleNext = [[None]*4 for _ in range(4)]
        self.grilleHold = [[None]*4 for _ in range(4)]
        #self.limiter_grille()
        #Pieces
        with open("dicoMatricesPiecesJolies.txt", "r") as fichier:
            dicoMatricesPiecesJolies = eval(fichier.read())
        self.dicoMatricesPieces = {}
        for (T, O), matrice in dicoMatricesPiecesJolies.items():
            lCoordonnees = []
            for dy in range(len(matrice)):
                for dx in range(len(matrice[dy])):
                    if matrice[dy][dx] == 1:
                        lCoordonnees.append((dx, dy))
            self.dicoMatricesPieces[(T, O)] = tuple(lCoordonnees)
        self.dicoCouleursPieces = {#type : couleur
                           "I" : (159, 209, 241),
                           "T" : (203, 167, 206),
                           "O" : (255, 230, 49),
                           "L" : (242, 164, 44),
                           "J" : (30, 122, 191),
                           "S" : (0, 171, 77),
                           "Z" : (216, 58, 44)}
        self.lTypePieces = ["I", "T", "O", "L", "J", "S", "Z"]
        self.lProchainesPieces = []
        self.holdPiece = None
        self.piece = None
        self.nextPiece = None
        self.holdUtilise = False
        self.lNbNoeuds = lNbNoeuds if lNbNoeuds is not None else [7, 1]#list(map(int, input("lNbNoeuds (ex : '7 8 1') : ").split())) if algorithme else None
        #algo
        self.algorithme = algorithme
        if self.algorithme :
            from TETRIS_algorithme_NN_v2 import Algorithme
            self.algo = Algorithme(jeu=self, lNbNoeuds=self.lNbNoeuds) #toujours vrai lui
            self.modeAlgo = False
            self.texteNbCoupsAlgo = None
        #DRL
        self.reset()
        self.entrainementGreedy = entrainementGreedy
        if self.entrainementGreedy and self.algorithme:
            self.entrainement_greedy()
        self.entrainementGenetique = entrainementGenetique
        if self.entrainementGenetique and self.algorithme:
            from TETRIS_algorithm_genetique_NN_v2 import Algorithme_Genetique
            self.algoGenetique = Algorithme_Genetique(jeu=self, algo=self.algo, lNbNoeuds=self.lNbNoeuds, tauxSurvivant=0.1, tauxRandom=0, nbLignes=self.nbLignes, nbColonnes=self.nbColonnes, modeCoups=3) if self.entrainementGenetique else None
            self.algoGenetique.entrainement()
        self.entrainementNES = entrainementNES
        if self.entrainementNES and self.algorithme and False:
            from TETRIS_NES_v1 import Neural_Evolution_Strategies
            self.nes = Neural_Evolution_Strategies(self, self.algo, self.lNbNoeuds[0]) if self.entrainementNES else None
            self.nes.entrainement(10, 30)
        self.entrainementDRL = entrainementDRL
        if self.entrainementDRL and self.algorithme and False:
            from TETRIS_DRL_v3 import Policy_Gradient
            self.pg = Policy_Gradient(self, self.algo, 1000, 30, self.nbCoupsMax, 1, self.lNbNoeuds[0], self.nbLignes, self.nbColonnes) if self.entrainementDRL else None
            self.pg.entrainement()

        self.menus = menus
        if self.menus :
            from menus_v3 import Menus
            self.menus = Menus(self, self.lAttributsPolice, self.horloge)
            self.menus.menuHome.actif = True
            self.menus.boucle()

        self.lTextes = (self.texteScore, self.texteNbCoups, self.texteSommeNbBlocs)
        if self.algorithme:
            self.lTextes += (self.texteNbCoupsAlgo)


    def reset(self, modeAlgo=False):
        self.finJeu = False
        self.iFrameAffichage = 0
        self.score = 0
        self.texteScore = None
        self.nbCoups = 0
        self.nbBlocs = 0
        self.sommeNbBlocs = 0
        #algo
        if self.algorithme:
            self.modeAlgo = modeAlgo
            self.algo.reset()
        #Grille
        assert not (modeAlgo and self.modeGrille != 0), f"Pas possible de lancer mode grille {self.modeGrille} avec algo activé..."
        self.lGrilles = [[[None]*self.nbColonnes for _ in range(self.nbLignes)] for __ in range(self.lDicoModesGrille[self.modeGrille]["nbGrilles"])]
        self.iGrille = 0
        self.grille = self.lGrilles[self.iGrille]
        self.grilleNext = [[None]*4 for _ in range(4)]
        self.grilleHold = [[None]*4 for _ in range(4)]
        #self.limiter_grille()
        #Pieces
        self.lProchainesPieces = []
        self.holdPiece = None
        self.piece = None
        self.nextPiece = None
        self.holdUtilise = False
        self.generer_piece()
        self.changer_score(gain=0)
        self.changer_nb_coups(deltaCoups=0)
        self.calculer_sommeNbBlocs(ajout=0)
        if self.algorithme:
            self.algo.changer_nb_coups(ajout=0)

    def tester_jeu(self, nbParties):
        for partie in range(1,nbParties+1):
            self.jouer(modeAlgo=False)
            print(f"Partie {partie} : Score {self.score} || Nb Coups : {self.nbCoups}")
            if self.quitterProgramme :
                break
            if self.menus:
                self.menus.menuGameOver.actif = True
                self.menus.boucle()

    def jouer(self, modeAlgo=False):
        self.reset(modeAlgo=modeAlgo)
        while not self.finJeu and not self.quitterProgramme:
            if self.algorithme and self.modeAlgo:
                for i in range(self.nbFramesAffichage):
                    self.algo.appliquer_position()
            else :
                self.piece.bouger(self.grille)
                self.tester_clavier()
            for event in pygame.event.get(): #ATTENTION à supprimer quand bot si on veut max perf
                if event.type == pygame.QUIT:
                    self.finJeu = True
                    self.quitterProgramme = True
                if event.type == pygame.KEYDOWN:
                    self.tester_clavier_appuie(event)
            if self.visuel :
                self.afficher()

    def afficher(self):
        self.fenetre.fill(self.couleurFond)

        if self.algorithme:
            self.algo.afficher_toutes_positions()
        tailleCases = self.lDicoModesGrille[self.modeGrille]["tailleCases"]
        xDebut, yDebut = self.lDicoModesGrille[self.modeGrille]["lXYDebut"][0]
        for iG, (grille, (xDebut, yDebut), orientation) in enumerate(zip(self.lGrilles, self.lDicoModesGrille[self.modeGrille]["lXYDebut"], self.lDicoModesGrille[self.modeGrille]["listeLOrientations"][self.iGrille])):
            piece = self.piece if iG == self.iGrille else None
            self.afficher_grille(grille, tailleCases, xDebut, yDebut, orientation=orientation, piece=piece, ombre=False, coin=False)
        self.afficher_grille(self.grilleNext, tailleCases, xDebut+tailleCases*(self.nbColonnes+1), yDebut+tailleCases*1, orientation=0, piece=self.nextPiece, ombre=False, coin=True)
        self.afficher_grille(self.grilleHold, tailleCases, xDebut-tailleCases*(4+1), yDebut+tailleCases*1, orientation=0, piece=self.holdPiece, ombre=False, coin=True)
        if self.algorithme:
            self.algo.desafficher_toutes_positions()

        xTexte = 10
        yTexte = 5
        for texte in self.lTextes:
            if texte == self.texteSommeNbBlocs and not self.calcul_sommeNbBlocs:
                continue
            self.fenetre.blit(texte, (xTexte, yTexte))
            w,h = texte.get_size()
            xTexte += (w + 30)

        pygame.display.update()

    def afficher_grille(self, grille, tailleCase, xDebut, yDebut, orientation, piece, ombre=False, coin=False):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        if piece is not None:
            if ombre :
                self.mettre_dans_grille(grille, piece.x, piece.yOmbre, piece.orientation, piece.type, (220,200,200), coin)
            self.mettre_dans_grille(grille, piece.x, piece.y, piece.orientation, piece.type, piece.couleur, coin)
        vx = self.lDXY[(orientation+1)%4]
        vy = self.lDXY[orientation]
        xFin = xDebut + tailleCase*(nbColonnes*vx[0] + nbLignes*vy[0])
        yFin = yDebut + tailleCase*(nbColonnes*vx[1] + nbLignes*vy[1])
        pygame.draw.rect(self.fenetre, self.couleurBorduresGrille, (min(xDebut, yFin)-(vx[0]+vy[0])*self.bordure*tailleCase, min(yDebut, yFin)-(vx[1]+vy[1])*self.bordure*tailleCase, abs(xFin-xDebut), abs(yFin-yDebut)))
        """for y in range(nbLignes):
            for x in range(nbColonnes):
                if grille[y][x] is not None:
                    r,g,b = grille[y][x] if grille[y][x] != False else (0,0,0)
                else :
                    r,g,b = self.couleurFondGrille
                x0 = xDebut + tailleCase*(x*vx[0] + y*vy[0])
                y0 = yDebut + tailleCase*(x*vx[1] + y*vy[1])
                x1 = x0 + tailleCase*(vx[0] + vy[0])
                y1 = y0 + tailleCase*(vx[1] + vy[1])
                #print(int(tailleCase), orientation, vx, vy, int(x0), int(y0), int(x1), int(y1))
                pygame.draw.rect(self.fenetre, (r,g,b), (min(x0, x1), min(y0, y1), abs(x1-x0), abs(y1-y0)))"""
        if piece is not None:
            if ombre :
                self.enlever_de_grille(grille, piece.x, piece.yOmbre, piece.orientation, piece.type, (220,200,200), coin)
            self.enlever_de_grille(grille, piece.x, piece.y, piece.orientation, piece.type, piece.couleur, coin)

    def changer_grille(self):
        self.iGrille = (self.iGrille+1)%self.lDicoModesGrille[self.modeGrille]["nbGrilles"]

    def changer_score(self, gain):
        self.score += gain
        self.texteScore = self.police.render(f"Score : {self.score}", False, self.couleurTextes)

    def changer_nb_coups(self, deltaCoups):
        self.nbCoups += deltaCoups
        self.texteNbCoups = self.police.render(f"Nb Coups : {self.nbCoups}", False, self.couleurTextes)
        if self.nbCoups >= self.nbCoupsMax :
            self.finJeu = True

    def changer_game_nb_coups_max(self, gameInfini):
        self.nbCoupsMax = 1e9 if gameInfini else 1000#int(input("nbCoupsMax : "))

    def changer_somme_nb_blocs(self, actif):
        self.calcul_sommeNbBlocs = actif

    def calculer_sommeNbBlocs(self, ajout):
        if not self.calcul_sommeNbBlocs:
            return
        self.nbBlocs += ajout
        self.sommeNbBlocs += self.nbBlocs
        self.texteSommeNbBlocs = self.police.render(f"Somme Nb Blocs : {self.sommeNbBlocs}", False, self.couleurTextes)

    def limiter_grille(self):
        for x in range(self.nbColonnes):
            self.grille[self.nbLignes-1][x] = (100,100,100)
        for y in range(self.nbLignes):
            self.grille[y][0] = (100,100,100)
            self.grille[y][self.nbColonnes-1] = (100,100,100)

    def generer_piece(self):
        if len(self.lProchainesPieces) < 3:
            bag7 = self.lTypePieces.copy()
            rd.shuffle(bag7)
            self.lProchainesPieces.extend(bag7)
        if not self.nextPiece:
            self.nextPiece = Tetromino(self, self.lProchainesPieces[-1])
            self.lProchainesPieces.pop()
        self.piece = self.nextPiece
        if self.piece.reset(self.grille):
            self.finJeu = True
        self.piece.predire_ombre(self.grille)
        self.nextPiece = Tetromino(self, self.lProchainesPieces[-1])
        self.lProchainesPieces.pop()
        self.holdUtilise = False

    def mettre_piece_hold(self):
        if self.holdUtilise:
            return
        self.holdUtilise = True
        if self.holdPiece is None:
            self.holdPiece = self.piece
            self.generer_piece()
        else :
            self.holdPiece, self.piece = self.piece, self.holdPiece
            if self.piece.reset(self.grille):
                self.finJeu = True
        self.piece.predire_ombre(self.grille)

    def tester_clavier(self):
        lTouchesAppuyees = pygame.key.get_pressed()
        if lTouchesAppuyees[pygame.K_DOWN]:
            self.piece.deltaTemps = self.piece.deltaTempsInit // 4
        else :
            self.piece.deltaTemps = self.piece.deltaTempsInit

    def tester_clavier_appuie(self, event):
        if event.key == pygame.K_SPACE:
            self.piece.deltaTemps = 0
            self.piece.deltaTempsInit = 0
        if event.key == pygame.K_UP:
            self.piece.tourner(self.grille, changement=1)
            if self.tester_chevauchement(self.grille, self.piece.x, self.piece.y, self.piece.orientation, self.piece.type):
                self.piece.tourner(self.grille, changement=-1)
        elif event.key == pygame.K_LEFT:
            self.piece.deplacer(self.grille, dx=-1)
            if self.tester_chevauchement(self.grille, self.piece.x, self.piece.y, self.piece.orientation, self.piece.type):
                self.piece.deplacer(self.grille, dx=1)
        elif event.key == pygame.K_RIGHT:
            self.piece.deplacer(self.grille, dx=1)
            if self.tester_chevauchement(self.grille, self.piece.x, self.piece.y, self.piece.orientation, self.piece.type):
                self.piece.deplacer(self.grille, dx=-1)
        elif event.key == pygame.K_h:
            self.mettre_piece_hold()
        elif event.key == pygame.K_p and self.algorithme: #positions
            self.algo.calculer_toutes_positions()
        elif event.key == pygame.K_a and self.algorithme: #appliquer position algo
            self.algo.appliquer_position()
        elif event.key == pygame.K_b and self.algorithme: #bot algo
            self.algo.changer_mode()
        elif event.key == pygame.K_c and self.algorithme: #nbCoups algo
            self.algo.changer_nb_coups(ajout=1)

    def tester_lignes(self, grille, reel=False, fScore=None):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        """dp = [0]*(nbLignes+1) #nbLignes à supprimer <= y
        for y in range(nbLignes-1, -1, -1):
            dp[y] = dp[y+1]
            if all(grille[y][x] is not None for x in range(nbColonnes)):
                dp[y] += 1
        nbLignesASupprimer = dp[0]
        if nbLignesASupprimer > 0:
            for y in range(nbLignes-1, -1, -1):
                if dp[y] == 0 :
                    continue
                elif y-dp[y] >= 0:
                    grille[y] = grille[y-dp[y]].copy()
                else :
                    grille[y] = [None]*nbColonnes"""
        grilleLignesPasCompletes = [ligne for ligne in grille if any(case is None for case in ligne)]
        nbLignesASupprimer = nbLignes-len(grilleLignesPasCompletes)
        if nbLignesASupprimer == 0:
            return grille
        grille2 = [[None]*nbColonnes for _ in range(nbLignesASupprimer)] + grilleLignesPasCompletes
        if reel :
            self.changer_score(gain=self.dicoScores[nbLignesASupprimer])
            self.calculer_sommeNbBlocs(ajout=-nbColonnes*nbLignesASupprimer)
        elif fScore is not None:
            fScore(gain=self.dicoScores[nbLignesASupprimer])
        return grille2

    def supprimer_ligne(self, grille, Y):
        for y in range(Y, 0, -1):
            grille[y] = grille[y-1].copy()
        for x in range(self.nbColonnes):
            grille[0][x] = None

    def tester_chevauchement(self, grille, X, Y, O, T, M=None):
        matrice = self.dicoMatricesPieces[(T, O)] if M is None else M
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for dx, dy in matrice:
            if not(0 <= X+dx < nbColonnes) or not(0 <= Y+dy < nbLignes) or (grille[Y+dy][X+dx] is not None):
                return True
        return False

    def mettre_dans_grille(self, grille, X, Y, O, T, C, coin, reel=True):
        matrice = self.dicoMatricesPieces[(T, O)]
        C = C if reel else False
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for dx, dy in matrice:
            if coin and (dx < nbColonnes) and (dy < nbLignes):
                grille[dy][dx] = C
            elif (0 <= X+dx < nbColonnes) and (0 <= Y+dy < nbLignes):
                grille[Y+dy][X+dx] = C

    def enlever_de_grille(self, grille, X, Y, O, T, C, coin):
        matrice = self.dicoMatricesPieces[(T, O)]
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for dx, dy in matrice:
            if coin and (dx < nbColonnes) and (dy < nbLignes):
                grille[dy][dx] = None
            elif (0 <= X+dx < nbColonnes) and (0 <= Y+dy < nbLignes):
                grille[Y+dy][X+dx] = None

    def entrainement_greedy(self):
        self.visuel = False
        self.changer_game_nb_coups_max(False)
        self.changer_somme_nb_blocs(False)
        nbParties = 10
        lConstantes = [0] * self.algo.nbConstantes
        #lConstantes = [0, 0, 0, 0.5, 0.5, 0.5]
        pasConstantes = 1
        nbCombinaisons = floor(1/pasConstantes + 1)**len(lConstantes)
        iCombinaison = 0
        dicoRes = {}
        while lConstantes[0] <= 1 and not self.quitterProgramme:
            iCombinaison += 1
            print(f"lConstantes = {lConstantes} || {iCombinaison} / {nbCombinaisons} ({round(iCombinaison/nbCombinaisons, 2) * 100}%)")
            self.algo.lConstantes = lConstantes
            sommeScores = 0
            sommeNbCoups = 0
            sommeSommeSommeNbBlocs = 0
            for i in range(nbParties):
                self.jouer(modeAlgo=True)
                #print(f"Partie {i+1} : Score {self.score}")
                sommeScores += self.score
                sommeNbCoups += self.nbCoups
                sommeSommeSommeNbBlocs += self.sommeNbBlocs
                if self.quitterProgramme :
                    break
            moyenneScores = sommeScores / nbParties
            moyenneNbCoups = sommeNbCoups / nbParties
            moyenneSommeSommeNbBlocs = sommeSommeSommeNbBlocs / nbParties
            print(f"==> scoreMoyen = {moyenneScores}")
            print(f"==> nbCoupsMoyen = {moyenneNbCoups}")
            print(f"==> moyenneSommeSommeNbBlocs = {moyenneSommeSommeNbBlocs}")
            dicoRes[tuple(lConstantes)] = (moyenneScores, moyenneNbCoups, moyenneSommeSommeNbBlocs)
            #Changement lConstantes
            iC = len(lConstantes)-1
            lConstantes[iC] += pasConstantes
            while iC > 0 and lConstantes[iC] > 1:
                lConstantes[iC] = 0
                iC -= 1
                lConstantes[iC] += pasConstantes
            if self.quitterProgramme :
                break
        with open("dico_comparatif_lConstantes.txt", "w") as fichier:
            fichier.write(str(dicoRes))
