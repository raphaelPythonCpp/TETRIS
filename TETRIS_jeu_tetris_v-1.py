# Créé par raphael.garivier, le 14/10/2025 en Python 3.7
from random import randint
import pygame
pygame.init()

largeurFenetre,hauteurFenetre = 500,800
fenetre = pygame.display.set_mode((largeurFenetre,hauteurFenetre))
pygame.display.set_caption("Jeu Tetris")

temps = pygame.time.Clock()

lImagesPieces = None#A REMPLIR
lCouleurs = [(255,0,0),(0,255,0),(0,0,255),(128,128,128)]
lDicoMatricesPieces = {
                       (1,0) : [[0,0,0],
                                [0,1,1],
                                [1,1,0]],
                       (1,1) : [[0,1,0],
                                [0,1,1],
                                [0,0,1]],
                       (1,2) : [[0,0,0],
                                [0,1,1],
                                [1,1,0]],
                       (1,3) : [[0,1,0],
                                [0,1,1],
                                [0,0,1]]
                       }

class Piece(object):
    def __init__(self,iPiece,x,y,orientation,couleur):
        #self.image = lImagesPieces[iPiece]
        self.iPiece = iPiece
        self.x = x
        self.y = y
        self.orientation = orientation
        lDicoMatricesPieces[(self.iPiece,self.orientation)]
        self.couleur = couleur

    def fixer(self):
        for y in range(3):
            for x in range(3):
                if self.matrice[y][x] != 0:
                    grille[self.y+y][self.x+x] = self.iPiece
        générer_piece()

    def descendre(self):
        global grille
        self.matrice = lDicoMatricesPieces[(self.iPiece,self.orientation)]
        for y in range(3):
            for x in range(3):
                if self.matrice[y][x] != 0 and grille[self.y+y+1][self.x+x] != 0:
                    self.fixer()
                    return "FIXAGE"
        self.y += 1

    def afficher(self):
        self.matrice = lDicoMatricesPieces[(self.iPiece,self.orientation)]
        for y in range(3):
            for x in range(3):
                if self.matrice[y][x] != 0:
                    pygame.draw.rect(fenetre,self.couleur,((self.x+x)*dx,yMin+(self.y+y)*dy,dx,dy))

def générer_piece():
    global lPieces,fin
    lPieces.append(Piece(1,randint(1,nbColonnes-2),0,randint(0,3),(randint(0,255),randint(0,255),randint(0,255))))
    lPieces[-1].matrice = lDicoMatricesPieces[(lPieces[-1].iPiece,lPieces[-1].orientation)]
    for y in range(3):
        for x in range(3):
            if lPieces[-1].matrice[y][x] != 0 and grille[lPieces[-1].y+y][lPieces[-1].x+x] != 0:
                fin = True


nbLignes,nbColonnes = 15,10
dy = dx = min(largeurFenetre,hauteurFenetre)//(nbColonnes+2)#max(nbLignes,nbColonnes)
xMin = dx
yMin = hauteurFenetre-dy*(nbLignes+1)
grille = [[-1]+[0]*(nbColonnes)+[-1] for _ in range(nbLignes)] + [[-1]*(nbColonnes+2)]
print(*grille)
"""grille = [[-1,0,0,0,0,0,0,0,0,-1],
          [-1,0,0,0,0,0,0,0,0,-1],
          [-1,0,0,0,0,0,0,0,0,-1],
          [-1,0,0,0,0,0,0,0,0,-1],
          [-1,0,0,0,0,0,0,0,0,-1],
          [-1,0,0,0,0,0,0,0,0,-1],
          [-1,0,0,0,0,0,0,0,0,-1],
          [-1,0,0,0,0,0,0,0,0,-1],
          [-1,0,0,0,0,0,0,0,0,-1],
          [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]"""
lPieces = []
générer_piece()
"""def remplir_grille():
    for y in range(nbLignes):
        for x in range(nbColonnes):"""


def remplir_ecran():
    #A REMPLIR PLUS TARD
    fenetre.fill((0,0,0))
    for y in range(nbLignes+1):
        for x in range(nbColonnes+2):
            if grille[y][x] != 0:
                pygame.draw.rect(fenetre,lCouleurs[grille[y][x]],(x*dx,yMin+y*dy,dx,dy))
    for piece in lPieces:
        piece.afficher()
    pygame.display.update()

fin = False
while not fin:
    temps.tick(20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            fin = True
    lPieces[-1].descendre()
    remplir_ecran()
pygame.quit()

for ligne in grille:
    print(*ligne)