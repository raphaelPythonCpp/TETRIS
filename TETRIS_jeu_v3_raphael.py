# Créé par raphael.garivier, le 24/02/2026 en Python 3.7
import pygame
import random as rd
from math import*

pygame.init()

wFenetre, hFenetre = 800, 800
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v3 Raphaël")

temps = pygame.time.Clock()

class Jeu(object):
    def __init__(self, tailleCase=50, nbColonnes=5, nbLignes = 8, visuel=True):
        self.finJeu = False
        self.visuel = visuel
        self.tailleCase = tailleCase
        self.bordure = 0.05
        self.nbColonnes, self.nbLignes = nbColonnes, nbLignes
        self.xDebutCases, self.yDebutCases = wFenetre/2 - nbColonnes/2*tailleCase, hFenetre/2 - nbLignes/2*tailleCase
        self.grille = [[None]*self.nbColonnes for _ in range(self.nbLignes)]
        self.grilleNext = [[None]*4 for _ in range(4)]
        self.grilleHold = [[None]*4 for _ in range(4)]
        self.limiter_grille()
        self.dicoMatricesPieces = {#(type, orientation (0->3) : matrice
                                    ("I", 0) : ((0,0,0,0),
                                                (1,1,1,1),
                                                (0,0,0,0),
                                                (0,0,0,0)),
                                    ("I", 1) : ((0,0,1,0),
                                                (0,0,1,0),
                                                (0,0,1,0),
                                                (0,0,1,0)),
                                    ("I", 2) : ((0,0,0,0),
                                                (0,0,0,0),
                                                (1,1,1,1),
                                                (0,0,0,0)),
                                    ("I", 3) : ((0,1,0,0),
                                                (0,1,0,0),
                                                (0,1,0,0),
                                                (0,1,0,0)),
                                    ("T", 0) : ((0,1,0),
                                                (1,1,1),
                                                (0,0,0)),
                                    ("T", 1) : ((0,1,0),
                                                (0,1,1),
                                                (0,1,0)),
                                    ("T", 2) : ((0,0,0),
                                                (1,1,1),
                                                (0,1,0)),
                                    ("T", 3) : ((0,1,0),
                                                (1,1,0),
                                                (0,1,0)),
                                    ("O", 0) : ((0,1,1),
                                                (0,1,1),
                                                (0,0,0)),
                                    ("O", 1) : ((0,1,1),
                                                (0,1,1),
                                                (0,0,0)),
                                    ("O", 2) : ((0,1,1),
                                                (0,1,1),
                                                (0,0,0)),
                                    ("O", 3) : ((0,1,1),
                                                (0,1,1),
                                                (0,0,0)),
                                    ("L", 0) : ((0,0,1),
                                                (1,1,1),
                                                (0,0,0)),
                                    ("L", 1) : ((0,1,0),
                                                (0,1,0),
                                                (0,1,1)),
                                    ("L", 2) : ((0,0,0),
                                                (1,1,1),
                                                (1,0,0)),
                                    ("L", 3) : ((1,1,0),
                                                (0,1,0),
                                                (0,1,0)),
                                    ("J", 0) : ((1,0,0),
                                                (1,1,1),
                                                (0,0,0)),
                                    ("J", 1) : ((0,1,1),
                                                (0,1,0),
                                                (0,1,0)),
                                    ("J", 2) : ((0,0,0),
                                                (1,1,1),
                                                (0,0,1)),
                                    ("J", 3) : ((0,1,0),
                                                (0,1,0),
                                                (1,1,0)),
                                    ("S", 0) : ((0,1,1),
                                                (1,1,0),
                                                (0,0,0)),
                                    ("S", 1) : ((0,1,0),
                                                (0,1,1),
                                                (0,0,1)),
                                    ("S", 2) : ((0,0,0),
                                                (0,1,1),
                                                (1,1,0)),
                                    ("S", 3) : ((1,0,0),
                                                (1,1,0),
                                                (0,1,0)),
                                    ("Z", 0) : ((1,1,0),
                                                (0,1,1),
                                                (0,0,0)),
                                    ("Z", 1) : ((0,0,1),
                                                (0,1,1),
                                                (0,1,0)),
                                    ("Z", 2) : ((0,0,0),
                                                (1,1,0),
                                                (0,1,1)),
                                    ("Z", 3) : ((0,1,0),
                                                (1,1,0),
                                                (1,0,0))
                                    }
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
        self.generer_piece()

    def jouer(self):
        self.generer_piece()
        self.finJeu = False
        while not self.finJeu:
            self.piece.bouger()
            self.tester_clavier()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finJeu = True
                if event.type == pygame.KEYDOWN:
                    self.tester_clavier_appuie(event)
            self.afficher()

    def afficher(self):
        fenetre.fill((255,255,155,255))

        self.afficher_grille(self.grille, self.tailleCase, self.xDebutCases, self.yDebutCases, piece=self.piece, ombre=True, coin=False)
        self.afficher_grille(self.grilleNext, self.tailleCase, self.xDebutCases+(self.nbColonnes+1)*self.tailleCase, self.yDebutCases, piece=self.nextPiece, ombre=False, coin=True)
        self.afficher_grille(self.grilleHold, self.tailleCase, self.xDebutCases+-5*self.tailleCase, self.yDebutCases, piece=self.holdPiece, ombre=False, coin=True)

        pygame.display.update()

    def afficher_grille(self, grille, tailleCase, xDebut, yDebut, piece, ombre=False, coin=False):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        if piece is not None:
            if ombre :
                piece.mettre_dans_grille(ombre=True, grille=grille, coin=coin)
            piece.mettre_dans_grille(ombre=False, grille=grille, coin=coin)
        pygame.draw.rect(fenetre, (255*0.9, 255*0.9, 255*0.9), (xDebut, yDebut, tailleCase*nbColonnes, tailleCase*nbLignes))
        for y in range(nbLignes):
            for x in range(nbColonnes):
               pygame.draw.rect(fenetre, (255,255,255), (xDebut+tailleCase*(x+self.bordure), yDebut+tailleCase*(y+self.bordure), tailleCase*(1-2*self.bordure), tailleCase*(1-self.bordure)))
        for y in range(nbLignes):
            for x in range(nbColonnes):
                if grille[y][x] is not None:
                    r,g,b = grille[y][x]
                    pygame.draw.rect(fenetre, (r,g,b), (xDebut+tailleCase*(x+self.bordure), yDebut+tailleCase*(y+self.bordure), tailleCase*(1-2*self.bordure), tailleCase*(1-2*self.bordure)))
        if piece is not None:
            piece.enlever_de_grille(ombre=False, grille=grille, coin=coin)
            if ombre :
                piece.enlever_de_grille(ombre=True, grille=grille, coin=coin)

    def limiter_grille(self):
        for x in range(self.nbColonnes):
            self.grille[self.nbLignes-1][x] = (100,100,100)
        for y in range(self.nbLignes):
            self.grille[y][0] = (100,100,100)
            self.grille[y][self.nbColonnes-1] = (100,100,100)

    def generer_piece(self):
        if not self.lProchainesPieces:
            self.lProchainesPieces = self.lTypePieces.copy()
            rd.shuffle(self.lProchainesPieces)
        if not self.nextPiece:
            self.nextPiece = Tetromino(self, self.lProchainesPieces[-1])
        self.piece = self.nextPiece
        self.piece.predire_ombre()
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
        self.holdPiece.reset()
        self.piece.predire_ombre()

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
            self.piece.tourner(1)
            if self.piece.tester_chevauchement(0):
                self.piece.tourner(-1)
        elif event.key == pygame.K_LEFT:
            self.piece.deplacer(-1)
            if self.piece.tester_chevauchement(0):
                self.piece.deplacer(1)
        elif event.key == pygame.K_RIGHT:
            self.piece.deplacer(1)
            if self.piece.tester_chevauchement(0):
                self.piece.deplacer(-1)
        elif event.key == pygame.K_h:
            self.mettre_piece_hold()

    def tester_lignes(self):
        y = 0
        while y < self.nbLignes-1:
            if all(val is not None for val in self.grille[y]):
                self.supprimer_ligne(y)
                y = 0
            else :
                y += 1

    def supprimer_ligne(self, Y):
        """for x in range(self.nbColonnes):
            self.grille[Y][x] = None
        for y in range(Y-1, -1, -1):
            for x in range(self.nbColonnes):
                y2 = y+1
                while y2+1 < self.nbLignes and self.grille[y2+1][x] is None:
                    y2 += 1
                self.grille[y2][x] = self.grille[y][x]
                self.grille[y][x] = None"""
        for y in range(Y, 0, -1):
            self.grille[y] = self.grille[y-1].copy()
        for x in range(self.nbColonnes):
            self.grille[0][x] = None
        self.grille[0][0] = (100,100,100)
        self.grille[0][self.nbColonnes-1] = (100,100,100)














class Tetromino(object):
    def __init__(self, jeu, type):
        self.jeu = jeu
        self.type = type
        self.couleur = self.jeu.dicoCouleursPieces[self.type]
        self.deltaTempsInit = 1000
        self.reset()

    def reset(self):
        self.orientation = rd.randint(0, 3)
        self.x = self.jeu.nbColonnes//2 - 1#rd.randint(0, self.jeu.nbColonnes-5)
        self.y = 0
        self.matrice = self.jeu.dicoMatricesPieces[(self.type, self.orientation)]
        self.tempsAvant = pygame.time.get_ticks()
        self.deltaTemps = self.deltaTempsInit #ms
        self.bouge = True
        self.yOmbre = 0

        if self.tester_chevauchement(dy=0):
            self.jeu.finJeu = True
        #self.predire_ombre()

    def bouger(self):
        self.enlever_de_grille()
        self.enlever_de_grille(ombre=True)
        if pygame.time.get_ticks() >= self.tempsAvant+self.deltaTemps:
            self.tempsAvant = pygame.time.get_ticks()
            self.descendre()
    def descendre(self, dy=1):
        if self.tester_chevauchement(dy=1) :
            self.fixer()
        else :
            self.y += 1

    def tester_chevauchement(self, dy=1, Y=None, X=None):
        if Y is None:
           Y = self.y
        if X is None:
           X = self.x
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    if not(0 <= Y+y+dy < self.jeu.nbLignes-1) or not(0 < X+x < self.jeu.nbColonnes-1):
                        #print("Hors limites")
                        return True
                    elif (self.jeu.grille[Y+y+dy][X+x] is not None):
                        #print("Chevauchement")
                        return True
        return False

    def enlever_de_grille(self, ombre=False, grille=None, coin=False):
        if grille is None:
            grille = self.jeu.grille
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    if ombre:
                        if coin :
                            grille[y][x] = None
                        else :
                            grille[self.yOmbre+y][self.x+x] = None
                    else :
                        if coin :
                            grille[y][x] = None
                        else :
                            grille[self.y+y][self.x+x] = None

    def mettre_dans_grille(self, ombre=False, grille=None, coin=False):
        if grille is None:
            grille = self.jeu.grille
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    if ombre:
                        if coin :
                            grille[y][x] = (220,220,200)
                        else :
                            grille[self.yOmbre+y][self.x+x] = (220, 220, 220)
                    else :
                        if coin:
                            grille[y][x] = self.couleur
                        else :
                            grille[self.y+y][self.x+x] = self.couleur

    def fixer(self):
        self.bouge = False
        self.yOmbre = None
        self.mettre_dans_grille()
        self.jeu.tester_lignes()
        self.jeu.generer_piece()

    def tourner(self, changement):
        self.orientation = (self.orientation + changement)%4
        self.matrice = self.jeu.dicoMatricesPieces[(self.type, self.orientation)]
        self.predire_ombre()

    def deplacer(self, dx):
        self.x += dx
        self.predire_ombre()

    def predire_ombre(self):
        self.yOmbre = self.y
        while not self.tester_chevauchement(dy=1, Y=self.yOmbre, X=self.x):
            self.yOmbre += 1

    def afficher(self, ombre=True, grille=None):
        if grille is None:
            grille = self.jeu.grille
        self.mettre_dans_grille(ombre=True, grille=grille)
        self.mettre_dans_grille(grille=grille)
        """
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    pygame.draw.rect(fenetre, self.couleur, (self.jeu.xDebutCases+self.jeu.tailleCase*(self.x+x), self.jeu.yDebutCases+self.jeu.tailleCase*(self.y+y), self.jeu.tailleCase, self.jeu.tailleCase))
                    pygame.draw.rect(fenetre, (220, 220, 220), (self.jeu.xDebutCases+self.jeu.tailleCase*(self.x+x), self.jeu.yDebutCases+self.jeu.tailleCase*(self.yOmbre+y), self.jeu.tailleCase, self.jeu.tailleCase))"""


env = Jeu(tailleCase=30, nbColonnes=10, nbLignes=16, visuel=True)
env.jouer()

pygame.quit()