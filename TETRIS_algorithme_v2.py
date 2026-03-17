from collections import deque
import pygame

dxy = [(1,0), (-1,0), (0,1)]
dxyo = [(1,0,0), (-1,0,0), (0,1,0), (0,0,1)]

class Algorithme(object):
    def __init__(self, jeu):
        #Graphiques
        self.dtAlgo = 0 #ms
        self.tAlgo = None
        #Calcul score
        self.jeu = jeu
        self.alpha = 0.0 #hauteur max grille
        self.beta = 0.2 #hauteur max piece
        self.gamma = 0.3 #somme hauteurs
        self.delta = 1 #nbTrous
        self.epsilon = 0.2 #irregularite
        self.lConstantes = [self.alpha, self.beta, self.gamma, self.delta, self.epsilon]
        self.nbConstantes = len(self.lConstantes)
    def reset(self):
        pass
    def calculer_toutes_positions(self, grille, piece):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        grillePositions = [[[False,False,False,False] for x in range(nbColonnes+4)] for y in range(nbLignes)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite
        xInit, yInit, oInit, tInit = piece.x, piece.y, piece.orientation, piece.type
        grillePositions[yInit][xInit+2][oInit] = True
        file = deque([(xInit+2, yInit, oInit)])
        print(file)
        while file:
            x,y,o = file.popleft()
            print(x,y,o)
            for dx,dy,do in dxyo :
                x2 = x+dx
                y2 = y+dy
                o2 = (o+do)%4
                if not self.jeu.tester_chevauchement(grille, x2-2, y2, o2, tInit) and not grillePositions[y2][x2][o2]:
                    grillePositions[y2][x2][o2] = True
                    file.append((x2,y2,o2))
        lPositions = []
        for y in range(nbLignes):
            for x in range(nbColonnes+4):
                for o in range(4):
                    if grillePositions[y][x][o]:
                        if self.jeu.tester_chevauchement(grille, x-2, y+1, o, tInit):
                            lPositions.append((x-2,y,o,tInit))
        lPositions.sort()
        return lPositions

    def hauteur_max_grille(self, grille):
        #Retourne l'indice de la ligne la plus haute avec un bloc
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for y in range(nbLignes):
            for x in range(nbColonnes):
                if grille[y][x] is not None:
                    return y
        return nbLignes-1

    def hauteur_max_piece(self, x, y, o, t):
        matrice = self.jeu.dicoMatricesPieces[(t, o)]
        nbLignes = len(matrice)
        nbColonnes = len(matrice[0])
        for dy in range(nbLignes):
            for dx in range(nbColonnes):
                if matrice[dy][dx] == 1:
                    return y+dy
        return y+len(matrice)

    def somme_hauteurs_grille(self, grille):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        sommeHauteurs = 0
        for y in range(nbLignes):
            for x in range(nbColonnes):
                if grille[y][x] is not None:
                    sommeHauteurs += 1
        return sommeHauteurs

    def nb_trous_cube(self, grille):
        #cube 1*1 qui fait une BFS
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        grilleVus = [[False]*nbColonnes for _ in range(nbLignes)]
        file = deque([])
        for x in range(nbColonnes):
            if grille[0][x] is None:
                file.append((x, 0))
                grilleVus[0][x] = True
        while file:
            x,y = file.popleft()
            for dx,dy in dxy:
                x2 = x+dx
                y2 = y+dy
                if (0 <= x2 < nbColonnes) and (0 <= y2 < nbLignes) and (grille[y2][x2] is None) and (not grilleVus[y2][x2]):
                    grilleVus[y2][x2] = True
                    file.append((x2,y2))
        nbTrous = 0
        for y in range(nbLignes):
            for x in range(nbColonnes):
                if (not grilleVus[y][x]) and (grille[y][x] is None):
                    nbTrous += 1
        return nbTrous

    def nb_trous_normal(self, grille):
        nbTrous = 0
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for x in range(nbColonnes):
            est_trou = False
            for y in range(1, nbLignes):
                if grille[y][x] is not None:
                    est_trou = True
                elif est_trou:
                    nbTrous += 1
        return nbTrous

    def irregularites(self, grille):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        nbIrregularites = 0
        yAvant = None
        for x in range(nbColonnes):
            y = -1
            while y+1 < nbLignes and grille[y+1][x] is None:
                y += 1
            if yAvant is None:
                yAvant = y
            nbIrregularites += abs(y-yAvant)
            yAvant = y
        return nbIrregularites

    def calculer_meilleure_position(self, grille, lPositions):
        lScores = [None]*len(lPositions)
        for iP,(x,y,o,t) in enumerate(lPositions):
            self.jeu.mettre_dans_grille(grille, x, y, o, t, self.jeu.dicoCouleursPieces[t], coin=False)
            lScores[iP] = self.calculer_score(grille, x, y, o, t)
            self.jeu.enlever_de_grille(grille, x, y, o, t, self.jeu.dicoCouleursPieces[t], coin=False)
        lMax = list(max(1e-20, max(abs(score[i]) for score in lScores if score[i] is not None)) for i in range(self.nbConstantes))
        scoreMax = -float("inf")
        meilleurePosition = (None,None,None,None) #(x,y,o,t)
        for iP,(x,y,o,t) in enumerate(lPositions):
            score = sum(lScores[iP][i]/lMax[i] * self.lConstantes[i] for i in range(self.nbConstantes))
            if score > scoreMax :
                scoreMax = score
                meilleurePosition = (x,y,o,t)
        return meilleurePosition

    def calculer_score(self, grille, x, y, o, t):
        score = [None]*self.nbConstantes
        score[0] = self.hauteur_max_grille(grille)
        score[1] = self.hauteur_max_piece(x, y, o, t)
        score[2] = self.somme_hauteurs_grille(grille)
        score[3] = -self.nb_trous_normal(grille)
        score[4] = -self.irregularites(grille)
        return score

    def appliquer_position(self, grille, piece, position):
        x,y,o,t = position
        piece.x = x
        piece.y = y
        piece.orientation = o
        piece.type = t
        piece.matrice = self.jeu.dicoMatricesPieces[(t,o)]
        piece.fixer()

    def jouer(self, grille, lPositionsPieces, piece):
        meilleurePosition = self.calculer_meilleure_position(grille, lPositionsPieces)
        self.appliquer_position(grille, piece, meilleurePosition)

    def boucle_jeu(self):
        if not self.jeu.modeAlgo :
            return
        if self.tAlgo+self.dtAlgo > pygame.time.get_ticks() :
            return
        self.tAlgo = pygame.time.get_ticks()
        self.jeu.tester_clavier_appuie(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))



    def afficher(self):
        print(self.score)