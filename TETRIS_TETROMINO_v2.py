import pygame
import random as rd

class Tetromino(object):
    def __init__(self, jeu, type):
        self.jeu = jeu
        self.type = type
        self.orientation = rd.randint(0, 3)
        self.matrice = self.jeu.dicoMatricesPieces[(self.type, self.orientation)]
        self.couleur = self.jeu.dicoCouleursPieces[self.type]
        self.deltaTempsInit = 1000
        self.x = self.jeu.nbColonnes//2 - 1
        if all(self.matrice[i][1] > 0 for i in range(len(self.matrice))):
            self.y = -1
        else :
            self.y = 0
        self.tempsAvant = pygame.time.get_ticks()
        self.deltaTemps = self.deltaTempsInit #ms
        self.bouge = True
        self.yOmbre = 0

    def reset(self, grille):
        self.x = self.jeu.nbColonnes//2 - 1
        if all(self.matrice[i][1] > 0 for i in range(len(self.matrice))):
            self.y = -1
        else :
            self.y = 0
        self.tempsAvant = pygame.time.get_ticks()
        self.deltaTemps = self.deltaTempsInit #ms
        self.bouge = True
        self.yOmbre = 0

        if self.jeu.tester_chevauchement(grille, self.x, self.y, self.orientation, self.type):
            return True
        return False

    def bouger(self, grille):
        if not self.bouge :
            return
        if pygame.time.get_ticks() >= self.tempsAvant+self.deltaTemps:
            self.tempsAvant = pygame.time.get_ticks()
            self.descendre(grille)
    def descendre(self, grille, dy=1):
        if self.jeu.tester_chevauchement(grille, self.x, self.y+1, self.orientation, self.type):
            self.fixer(grille, tester_lignes=True, reel=True)
        else :
            self.y += 1

    def fixer(self, grille, tester_lignes=True, reel=True, fScore=None):
        self.bouge = False
        self.yOmbre = None
        """self.jeu.afficher()
        pygame.time.delay(500)"""
        self.jeu.mettre_dans_grille(grille, self.x, self.y, self.orientation, self.type, self.couleur, coin=False, reel=reel)
        if tester_lignes:
            self.jeu.tester_lignes(grille, reel=reel, fScore=fScore)
        if reel:
            self.jeu.changer_nb_coups(deltaCoups=1)
            self.jeu.calculer_sommeNbBlocs(ajout=4) #ATTENTION A modifier si tetromino plus seulement de 4 pièces
            self.jeu.generer_piece()

    def tourner(self, grille, changement):
        self.orientation = (self.orientation + changement)%4
        self.matrice = self.jeu.dicoMatricesPieces[(self.type, self.orientation)]
        self.predire_ombre(grille)

    def deplacer(self, grille, dx):
        self.x += dx
        self.predire_ombre(grille)

    def predire_ombre(self, grille):
        self.yOmbre = self.y
        while not self.jeu.tester_chevauchement(grille, self.x, self.yOmbre+1, self.orientation, self.type):
            self.yOmbre += 1