# Créé par raphael.garivier, le 24/02/2026 en Python 3.7
import pygame
import random as rd

pygame.init()

wFenetre, hFenetre = 400, 800
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v1 Raphaël")

temps = pygame.time.Clock()

class Jeu(object):
    def __init__(self, tailleCase=50, visuel=True):
        self.finJeu = False
        self.visuel = visuel
        self.tailleCase = tailleCase
        self.bordure = 0.05
        self.nbColonnes, self.nbLignes = wFenetre//self.tailleCase, hFenetre//self.tailleCase
        self.xDebutCases, self.yDebutCases = 0, 0
        self.grille = [[None]*self.nbColonnes for _ in range(self.nbLignes)]
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
        self.piece = None
        self.generer_piece()

    def jouer(self):
        self.generer_piece()
        self.finJeu = False
        while not self.finJeu:
            self.piece.bouger()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.finJeu = True
                if event.type == pygame.KEYDOWN:
                    self.tester_clavier(event)
            self.remplir_ecran()

    def remplir_ecran(self):
        fenetre.fill((255,255,255))
        self.piece.afficher()
        for y in range(self.nbLignes):
            for x in range(self.nbColonnes):
                if self.grille[y][x] is not None:
                   r,g,b = self.grille[y][x]
                   pygame.draw.rect(fenetre, self.grille[y][x], (self.xDebutCases+self.tailleCase*x, self.yDebutCases+self.tailleCase*y, self.tailleCase, self.tailleCase))
                   pygame.draw.rect(fenetre, (0.5*r,0.5*g,0.5*b), (self.xDebutCases+self.tailleCase*(x-self.bordure), self.yDebutCases+self.tailleCase*(y-self.bordure), self.tailleCase*2*self.bordure, self.tailleCase*(1+2*self.bordure)))
                   pygame.draw.rect(fenetre, (0.5*r,0.5*g,0.5*b), (self.xDebutCases+self.tailleCase*(x+1-self.bordure), self.yDebutCases+self.tailleCase*(y-self.bordure), self.tailleCase*2*self.bordure, self.tailleCase*(1+2*self.bordure)))
                   pygame.draw.rect(fenetre, (0.5*r,0.5*g,0.5*b), (self.xDebutCases+self.tailleCase*(x-self.bordure), self.yDebutCases+self.tailleCase*(y-self.bordure), self.tailleCase*(1+2*self.bordure), self.tailleCase*2*self.bordure))
                   pygame.draw.rect(fenetre, (0.5*r,0.5*g,0.5*b), (self.xDebutCases+self.tailleCase*(x-self.bordure), self.yDebutCases+self.tailleCase*(y+1-self.bordure), self.tailleCase*(1+2*self.bordure), self.tailleCase*2*self.bordure))
        pygame.display.update()

    def generer_piece(self):
        if not self.lProchainesPieces:
            self.lProchainesPieces = self.lTypePieces.copy()
            rd.shuffle(self.lProchainesPieces)
        self.piece = Piece(self, self.lProchainesPieces[-1])
        self.lProchainesPieces.pop()

    def tester_clavier(self, event):
        if event.key == pygame.K_SPACE:
            self.piece.nbImages //= 8
        if event.key == pygame.K_UP:
            self.piece.tourner(-1)
            if self.piece.tester_chevauchement(0):
                self.piece.tourner(1)
        elif event.key == pygame.K_DOWN:
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

    def tester_lignes(self):
        y = 0
        while y < self.nbLignes:
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

class Piece(object):
    def __init__(self, jeu, type):
        self.jeu = jeu
        self.type = type
        self.orientation = rd.randint(0, 3)
        self.x = rd.randint(0, self.jeu.nbColonnes-5)
        self.y = 0
        self.couleur = self.jeu.dicoCouleursPieces[self.type]
        self.matrice = self.jeu.dicoMatricesPieces[(self.type, self.orientation)]
        self.image = 0
        self.nbImages = 512
        self.bouge = True
        self.yOmbre = 0

        if self.tester_chevauchement(0):
            self.jeu.finJeu = True
        self.predire_ombre()

    def bouger(self):
        self.enlever_de_grille()
        self.enlever_de_grille(ombre=True)
        self.image += 1
        if self.image >= self.nbImages:
            self.descendre()
            self.image = 0

    def descendre(self, dy=1):
        fin = self.tester_chevauchement(1)
        if fin :
            self.fixer()
        else :
            self.y += 1
            self.predire_ombre()

    def tester_chevauchement(self, dy=1):
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    if not(0 <= self.y+y+dy < self.jeu.nbLignes) or not(0 <= self.x+x < self.jeu.nbColonnes) or self.jeu.grille[self.y+y+dy][self.x+x] is not None:
                        return True
        return False

    def enlever_de_grille(self, ombre=False):
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    if ombre:
                        self.jeu.grille[self.yOmbre+y][self.x+x] = None
                    else :
                        self.jeu.grille[self.y+y][self.x+x] = None

    def mettre_dans_grille(self, ombre=False):
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    if ombre:
                        self.jeu.grille[self.yOmbre+y][self.x+x] = (220, 220, 220)
                    else :
                        self.jeu.grille[self.y+y][self.x+x] = self.couleur

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
        yAvant = self.y
        while not self.tester_chevauchement(1):
            self.y += 1
        self.yOmbre = self.y
        self.y = yAvant

    def afficher(self, ombre=True):
        self.mettre_dans_grille(ombre=True)
        self.mettre_dans_grille()
        """
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    pygame.draw.rect(fenetre, self.couleur, (self.jeu.xDebutCases+self.jeu.tailleCase*(self.x+x), self.jeu.yDebutCases+self.jeu.tailleCase*(self.y+y), self.jeu.tailleCase, self.jeu.tailleCase))
                    pygame.draw.rect(fenetre, (220, 220, 220), (self.jeu.xDebutCases+self.jeu.tailleCase*(self.x+x), self.jeu.yDebutCases+self.jeu.tailleCase*(self.yOmbre+y), self.jeu.tailleCase, self.jeu.tailleCase))"""


env = Jeu()
env.jouer()

pygame.quit()