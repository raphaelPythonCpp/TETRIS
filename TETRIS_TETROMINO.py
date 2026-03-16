import pygame
import random as rd

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

        if self.jeu.tester_chevauchement(self.jeu.grille, self.x, self.y, self.orientation, self.type):
            self.jeu.finJeu = True
        #self.predire_ombre()

    def bouger(self):
        if not self.bouge :
            return
        if pygame.time.get_ticks() >= self.tempsAvant+self.deltaTemps:
            self.tempsAvant = pygame.time.get_ticks()
            self.descendre()
    def descendre(self, dy=1):
        if self.jeu.tester_chevauchement(self.jeu.grille, self.x, self.y+1, self.orientation, self.type):
            self.fixer()
        else :
            self.y += 1

    def fixer(self):
        self.bouge = False
        self.yOmbre = None
        self.jeu.mettre_dans_grille(self.jeu.grille, self.x, self.y, self.orientation, self.type, self.couleur, coin=False)
        self.jeu.tester_lignes(self.jeu.grille)
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
        while not self.jeu.tester_chevauchement(self.jeu.grille, self.x, self.yOmbre+1, self.orientation, self.type):
            self.yOmbre += 1

    """def afficher(self, ombre=True, grille=None):
        if grille is None:
            grille = self.jeu.grille
        self.mettre_dans_grille(ombre=True, grille=grille)
        self.mettre_dans_grille(grille=grille)""""""
        for y in range(len(self.matrice)):
            for x in range(len(self.matrice[y])):
                if self.matrice[y][x] == 1:
                    pygame.draw.rect(fenetre, self.couleur, (self.jeu.xDebutCases+self.jeu.tailleCase*(self.x+x), self.jeu.yDebutCases+self.jeu.tailleCase*(self.y+y), self.jeu.tailleCase, self.jeu.tailleCase))
                    pygame.draw.rect(fenetre, (220, 220, 220), (self.jeu.xDebutCases+self.jeu.tailleCase*(self.x+x), self.jeu.yDebutCases+self.jeu.tailleCase*(self.yOmbre+y), self.jeu.tailleCase, self.jeu.tailleCase))"""
