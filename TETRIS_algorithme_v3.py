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
        self.zeta = 1 #lignes
        self.lConstantes = [self.alpha, self.beta, self.gamma, self.delta, self.epsilon, self.zeta]
        self.nbConstantes = len(self.lConstantes)
    def reset(self):
        pass

    def calculer_toutes_positions(self, grille, piece1, piece2):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])

        #Partie1 : Piece normale
        grillePositions = [[[False,False,False,False] for x in range(nbColonnes+4)] for y in range(nbLignes)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite
        xInit1, yInit1, oInit1, tInit1 = piece1.x, piece1.y, piece1.orientation, piece1.type
        grillePositions[yInit1][xInit1+2][oInit1] = True
        file = deque([(xInit1+2, yInit1, oInit1)])
        while file:
            x,y,o = file.popleft()
            for dx,dy,do in dxyo :
                x2 = x+dx
                y2 = y+dy
                o2 = (o+do)%4
                if not self.jeu.tester_chevauchement(grille, x2-2, y2, o2, tInit1) and not grillePositions[y2][x2][o2]:
                    grillePositions[y2][x2][o2] = True
                    file.append((x2,y2,o2))
        lPositions1 = []
        for y in range(nbLignes):
            for x in range(nbColonnes+4):
                for o in range(4):
                    if grillePositions[y][x][o]:
                        if self.jeu.tester_chevauchement(grille, x-2, y+1, o, tInit):
                            lPositions1.append((x-2,y,o,tInit1))

        #Partie2 : Piece suiviante
        lPositions2 = []
        for x1,y1,o1,t1 in lPositions1:
            self.jeu.mettre_dans_grille(grille, x1, y1, o1, t1, (0,0,0), False)
            grillePositions = [[[False,False,False,False] for x in range(nbColonnes+4)] for y in range(nbLignes)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite
            xInit2, yInit2, oInit2, tInit2 = piece2.x, piece2.y, piece2.orientation, piece2.type
            grillePositions[yInit2][xInit2+2][oInit2] = True
            file = deque([(xInit2+2, yInit2, oInit2)])
            while file:
                x,y,o = file.popleft()
                for dx,dy,do in dxyo :
                    x2 = x+dx
                    y2 = y+dy
                    o2 = (o+do)%4
                    if not self.jeu.tester_chevauchement(grille, x2-2, y2, o2, tInit2) and not grillePositions[y2][x2][o2]:
                        grillePositions[y2][x2][o2] = True
                        file.append((x2,y2,o2))
            for y in range(nbLignes):
                for x in range(nbColonnes+4):
                    for o in range(4):
                        if grillePositions[y][x][o]:
                            if self.jeu.tester_chevauchement(grille, x-2, y+1, o, tInit):
                                lPositions2.append((x1,y1,o1,t1,x-2,y,o,tInit2))
            self.jeu.enlever_de_grille(grille, x1, y1, o1, t1, None, False)
        lPositions2.sort()
        return lPositions2

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

    def nb_lignes(self, grille):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        nbLignesASupprimer = 0
        for y in range(nbLignes):
            if all([grille[y][x] is not None for x in range(nbColonnes)]):
                nbLignesASupprimer += 1
        return nbLignesASupprimer

    def calculer_meilleure_position(self, grille, lPositions):
        lScores = [None]*len(lPositions)
        for iP,(x1,y1,o1,t1,x2,y2,o2,t2) in enumerate(lPositions):
            self.jeu.mettre_dans_grille(grille, x1, y1, o1, t1, self.jeu.dicoCouleursPieces[t1], coin=False)
            self.jeu.mettre_dans_grille(grille, x2, y2, o2, t2, self.jeu.dicoCouleursPieces[t2], coin=False)
            lScores[iP] = self.calculer_score(grille, x1, y1, o1, t1, x2, y2, o2, t2)
            self.jeu.enlever_de_grille(grille, x1, y1, o1, t1, None, coin=False)
            self.jeu.enlever_de_grille(grille, x2, y2, o2, t2, None, coin=False)
        lMax = list(max(1e-20, max(abs(score[i]) for score in lScores if score[i] is not None)) for i in range(self.nbConstantes))
        scoreMax = -float("inf")
        meilleurePosition = (None,None,None,None) #(x,y,o,t)
        for iP,position in enumerate(lPositions):
            score = sum(lScores[iP][i]/lMax[i] * self.lConstantes[i] for i in range(self.nbConstantes))
            if score > scoreMax :
                scoreMax = score
                meilleurePosition = position
        return meilleurePosition

    def calculer_score(self, grille, x1, y1, o1, t1, x2, y2, o2, t2):
        score = [None]*self.nbConstantes
        score[0] = self.hauteur_max_grille(grille)
        score[1] = self.hauteur_max_piece(x1, y1, o1, t1) + self.hauteur_max_piece(x2, y2, o2, t2)
        score[2] = self.somme_hauteurs_grille(grille)
        score[3] = -self.nb_trous_normal(grille)
        score[4] = -self.irregularites(grille)
        score[5] = self.nb_lignes(grille)
        return score

    def appliquer_position(self, grille, piece1, position1, piece2, position2):
        #Piece 1
        x1,y1,o1,t1 = position1
        piece1.x = x1
        piece1.y = y1
        piece1.orientation = o1
        piece1.type = t1
        piece1.matrice = self.jeu.dicoMatricesPieces[(t1,o1)]
        piece1.fixer()
        #Piece 2
        x2,y2,o2,t2 = position2
        piece2.x = x2
        piece2.y = y2
        piece2.orientation = o2
        piece2.type = t2
        piece2.matrice = self.jeu.dicoMatricesPieces[(t2,o2)]
        piece2.fixer()

    def jouer(self, grille, lPositionsPieces, piece1, piece2):
        meilleurePosition = self.calculer_meilleure_position(grille, lPositionsPieces)
        self.appliquer_position(grille, piece1, meilleurePosition[:4], piece2, meilleurePosition[4:])

    def boucle_jeu(self):
        if not self.jeu.modeAlgo :
            return
        if self.tAlgo+self.dtAlgo > pygame.time.get_ticks() :
            return
        self.tAlgo = pygame.time.get_ticks()
        self.jeu.tester_clavier_appuie(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))


    def afficher(self):
        print(self.score)