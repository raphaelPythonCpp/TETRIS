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
        self.reset()

    def reset(self):
        self.x = self.jeu.nbColonnes//2 - 1
        if all(self.matrice[0][x] == 0 for x in range(len(self.matrice[0]))):
            self.y = -1
        else :
            self.y = 0
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

    def fixer(self, tester_lignes=True):
        self.bouge = False
        self.yOmbre = None
        self.jeu.mettre_dans_grille(self.jeu.grille, self.x, self.y, self.orientation, self.type, self.couleur, coin=False)
        if tester_lignes:
            self.jeu.tester_lignes(self.jeu.grille, reel=True)
        self.jeu.changer_nb_coups(deltaCoups=1)
        self.jeu.calculer_sommeNbBlocs(ajout=4) #ATTENTION A modifier si tetromino plus seulement de 4 pièces
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