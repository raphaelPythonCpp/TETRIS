# Créé par raphael.garivier, le 24/02/2026 en Python 3.7
import pygame
import random as rd

pygame.init()

wFenetre, hFenetre = 400, 800
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v1 Raphaël")

temps = pygame.time.Clock()

tailleCase = 50
nbColonnes, nbLignes = wFenetre//tailleCase, hFenetre//tailleCase
xDebutCases, yDebutCases = 0, 0
"""grille = [  [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,None,None,None,None,None,None],
            [None,None,(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0)]]"""
grille = [[None]*nbColonnes for _ in range(nbLignes)]

dicoMatricesPieces = {#(type, orientation (0->3) : matrice
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
dicoCouleursPieces = {#type : couleur
                   "I" : (159, 209, 241),
                   "T" : (203, 167, 206),
                   "O" : (255, 230, 49),
                   "L" : (242, 164, 44),
                   "J" : (30, 122, 191),
                   "S" : (0, 171, 77),
                   "Z" : (216, 58, 44)}
lTypePieces = ["I", "T", "O", "L", "J", "S", "Z"]
class Piece(object):
    def __init__(self, type):
        self.type = type
        self.orientation = rd.randint(0, 3)
        self.x = rd.randint(0, nbColonnes-5)
        self.y = 0
        self.couleur = dicoCouleursPieces[self.type]
        self.matrice = dicoMatricesPieces[(self.type, self.orientation)]
        self.image = 0
        self.nbImages = 512
        self.bouge = True
        self.yOmbre = 0

        if self.tester_chevauchement(0):
            global finJeu
            finJeu = True
        self.predire_ombre()

    def bouger(self):
        if not self.bouge:
            return
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
                    if not(0 <= self.y+y+dy < nbLignes) or not(0 <= self.x+x < nbColonnes) or grille[self.y+y+dy][self.x+x] is not None:
                        return True
        return False

    def fixer(self):
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    grille[self.y+y][self.x+x] = self.couleur
        self.bouge = False
        self.yOmbre = None
        tester_lignes()
        generer_piece()

    def tourner(self, changement):
        lPieces[-1].orientation = (lPieces[-1].orientation + changement)%4
        lPieces[-1].matrice = dicoMatricesPieces[(lPieces[-1].type, lPieces[-1].orientation)]
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
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    pygame.draw.rect(fenetre, self.couleur, (xDebutCases+tailleCase*(self.x+x), yDebutCases+tailleCase*(self.y+y), tailleCase, tailleCase))
                    pygame.draw.rect(fenetre, (220, 220, 220), (xDebutCases+tailleCase*(self.x+x), yDebutCases+tailleCase*(self.yOmbre+y), tailleCase, tailleCase))

def generer_piece():
    lPieces.append(Piece(rd.choice(lTypePieces)))

def tester_clavier(event):
    if event.key == pygame.K_SPACE:
        lPieces[-1].nbImages //= 4
    if event.key == pygame.K_UP:
        lPieces[-1].tourner(-1)
        if lPieces[-1].tester_chevauchement(0):
            lPieces[-1].tourner(1)
    elif event.key == pygame.K_DOWN:
        lPieces[-1].tourner(1)
        if lPieces[-1].tester_chevauchement(0):
            lPieces[-1].tourner(-1)
    elif event.key == pygame.K_LEFT:
        lPieces[-1].deplacer(-1)
        if lPieces[-1].tester_chevauchement(0):
            lPieces[-1].deplacer(1)
    elif event.key == pygame.K_RIGHT:
        lPieces[-1].deplacer(1)
        if lPieces[-1].tester_chevauchement(0):
            lPieces[-1].deplacer(-1)

def tester_lignes():
    y = 0
    while y < nbLignes:
        if all(val is not None for val in grille[y]):
            supprimer_ligne(y)
            y = 0
        else :
            y += 1

def supprimer_ligne(Y):
    for x in range(nbColonnes):
        grille[Y][x] = None
    for y in range(Y-1, -1, -1):
        for x in range(nbColonnes):
            y2 = y+1
            while y2+1 < nbLignes and grille[y2+1][x] is None:
                y2 += 1
            grille[y2][x] = grille[y][x]
            grille[y][x] = None
    for x in range(nbColonnes):
        grille[0][x] = None

lPieces = []
generer_piece()

def remplir_ecran():
    fenetre.fill((255,255,255))
    for y in range(nbLignes):
        for x in range(nbColonnes):
            if grille[y][x] is not None:
               pygame.draw.rect(fenetre, grille[y][x], (xDebutCases+tailleCase*x, yDebutCases+tailleCase*y, tailleCase, tailleCase))
    lPieces[-1].afficher()
    pygame.display.update()

finJeu = False
while not finJeu:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finJeu = True
        if event.type == pygame.KEYDOWN:
            tester_clavier(event)
    lPieces[-1].bouger()
    remplir_ecran()
pygame.quit()
