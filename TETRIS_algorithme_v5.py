from collections import deque
import pygame

dxy = [(1,0), (-1,0), (0,1)]
dxyo = [(1,0,0), (-1,0,0), (0,1,0), (0,0,1)]

class Algorithme(object):
    def __init__(self, jeu):
        #Graphiques
        self.dtAlgo = 0 #ms
        self.tAlgo = None
        self.nbCoups = 3 #{1 : piece, 2 : piece+nextPiece, 3 : piece+holdPiece}
        self.nbCoupsMax = 3
        #Calcul score
        self.jeu = jeu
        self.alpha = 1 #hauteur max grille
        self.beta = 0 #hauteur max piece
        self.gamma = 0. #somme hauteurs
        self.delta = 1 #nbTrous
        self.epsilon = 1 #irregularite
        self.zeta = 1 #lignes
        self.lConstantes = [self.alpha, self.beta, self.gamma, self.delta, self.epsilon, self.zeta]
        self.nbConstantes = len(self.lConstantes)
        #Positions prédites
        self.lPositionsPieces = []
        self.visuelPositions = False
        self.iPosition = 0
        self.dtPositionsInit = 100 #ms
        self.tPositionsAvant = pygame.time.get_ticks()
    def reset(self):
        #Positions prédites
        self.visuelPositions = False
        self.lPositionsPieces = []
        self.iPosition = 0
        self.tPositionsAvant = pygame.time.get_ticks()

    def changer_mode(self):
        if not self.jeu.modeAlgo:
            self.tAlgo = pygame.time.get_ticks()
        self.jeu.modeAlgo = not self.jeu.modeAlgo

    def calculer_toutes_positions(self):
        if self.nbCoups == 1:
            self.lPositionsPieces = self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.piece)
        elif self.nbCoups == 2 :
            self.jeu.nextPiece.reset()
            self.lPositionsPieces = self.calculer_toutes_positions_2_coups(self.jeu.grille, self.jeu.piece, self.jeu.nextPiece)
        elif self.nbCoups == 3:
            if self.jeu.holdPiece is None:
                self.jeu.mettre_piece_hold()
            self.jeu.holdPiece.reset()
            self.lPositionsPieces = [self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.piece), self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.holdPiece)]
        self.changer_visuel_positions()

    def calculer_toutes_positions_2_coups(self, grille, piece1, piece2):
        #BFS sur les 2 pièces puis merge des solutions sans overlap de p1 et p2
        nbLignes = len(grille)
        nbColonnes = len(grille[0])

        #Partie1 : Piece normale
        grillePositions = [[0b0000 for x in range(nbColonnes+4)] for y in range(nbLignes)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite
        xInit1, yInit1, oInit1, tInit1 = piece1.x, piece1.y, piece1.orientation, piece1.type
        grillePositions[yInit1][xInit1+2] |= (1 << oInit1)
        file = deque([(xInit1+2, yInit1, oInit1)])
        while file:
            x,y,o = file.popleft()
            for dx,dy,do in dxyo :
                x2 = x+dx
                y2 = y+dy
                o2 = (o+do)%4
                if not self.jeu.tester_chevauchement(grille, x2-2, y2, o2, tInit1) and not ((grillePositions[y2][x2] >> o2) & 1):
                    grillePositions[y2][x2] |= (1 << o2)
                    file.append((x2,y2,o2))
        lPositions1 = []
        for y in range(nbLignes):
            for x in range(nbColonnes+4):
                for o in range(4):
                    if (grillePositions[y][x] >> o) & 1:
                        if self.jeu.tester_chevauchement(grille, x-2, y+1, o, tInit1):
                            lPositions1.append((x-2,y,o,tInit1))

        #Partie2 : Piece suiviante
        lPositions2 = []
        grillePositions = [[0b0000 for x in range(nbColonnes+4)] for y in range(nbLignes)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite
        xInit2, yInit2, oInit2, tInit2 = piece2.x, piece2.y, piece2.orientation, piece2.type
        grillePositions[yInit2][xInit2+2] |= (1 << oInit2)
        file = deque([(xInit2+2, yInit2, oInit2)])
        while file:
            x,y,o = file.popleft()
            for dx,dy,do in dxyo :
                x2 = x+dx
                y2 = y+dy
                o2 = (o+do)%4
                if not self.jeu.tester_chevauchement(grille, x2-2, y2, o2, tInit2) and not ((grillePositions[y2][x2] >> o2) & 1):
                    grillePositions[y2][x2]|= (1 << o2)
                    file.append((x2,y2,o2))
        for y in range(nbLignes):
            for x in range(nbColonnes+4):
                for o in range(4):
                    if (grillePositions[y][x] >> o) & 1:
                        if self.jeu.tester_chevauchement(grille, x-2, y+1, o, tInit2):
                            lPositions2.append((x-2,y,o,tInit2))

        #Merge des 2 BFS
        lPositionsFinales = []
        for x1,y1,o1,t1 in lPositions1:
            self.jeu.mettre_dans_grille(grille, x1, y1, o1, t1, (0,0,0), False)
            for x2,y2,o2,t2 in lPositions2:
                if not self.jeu.tester_chevauchement(grille, x2, y2, o2, t2):
                    lPositionsFinales.append((x1,y1,o1,t1,x2,y2,o2,t2))
            self.jeu.enlever_de_grille(grille, x1, y1, o1, t1, None, False)
        lPositionsFinales.sort()
        return lPositionsFinales

    def calculer_toutes_positions_1_coup(self, grille, piece):
        #BFS sur la piece
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        grillePositions = [[0b0000 for x in range(nbColonnes+4)] for y in range(nbLignes)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite
        xInit, yInit, oInit, tInit = piece.x, piece.y, piece.orientation, piece.type
        grillePositions[yInit][xInit+2] |= (1 << oInit)
        file = deque([(xInit+2, yInit, oInit)])
        while file:
            x,y,o = file.popleft()
            for dx,dy,do in dxyo :
                x2 = x+dx
                y2 = y+dy
                o2 = (o+do)%4
                if not self.jeu.tester_chevauchement(grille, x2-2, y2, o2, tInit) and not ((grillePositions[y2][x2] >> o2) & 1):
                    grillePositions[y2][x2] |= (1 << o2)
                    file.append((x2,y2,o2))
        lPositions = []
        for y in range(nbLignes):
            for x in range(nbColonnes+4):
                for o in range(4):
                    if (grillePositions[y][x] >> o) & 1:
                        if self.jeu.tester_chevauchement(grille, x-2, y+1, o, tInit):
                            lPositions.append((x-2,y,o,tInit))
        #keep que les solutions valides
        lPositionsFinales = []
        for x,y,o,t in lPositions:
            if not self.jeu.tester_chevauchement(grille, x, y, o, t):
                lPositionsFinales.append((x,y,o,t))
        lPositionsFinales.sort()
        return lPositionsFinales

    def hauteur_max_grille(self, grille):
        #Retourne l'indice de la ligne la plus haute avec un bloc
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for y in range(nbLignes):
            for x in range(nbColonnes):
                if grille[y][x] is not None:
                    return nbLignes-1-y
        return nbLignes

    def hauteur_max_piece(self, x, y, o, t):
        matrice = self.jeu.dicoMatricesPieces[(t, o)]
        nbLignes = len(matrice)
        nbColonnes = len(matrice[0])
        for dy in range(nbLignes):
            for dx in range(nbColonnes):
                if matrice[dy][dx] == 1:
                    return nbLignes-1-(y+dy)
        return nbLignes

    def somme_hauteurs_grille(self, grille):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        sommeHauteurs = 0
        for x in range(nbColonnes):
            for y in range(nbLignes):
                if grille[y][x] is not None:
                    sommeHauteurs += (nbLignes-1-y)
                    break
            else :
                sommeHauteurs += nbLignes
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
            y = 0
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
            if all(grille[y][x] is not None for x in range(nbColonnes)):
                nbLignesASupprimer += 1
        return nbLignesASupprimer

    def calculer_meilleure_position_2_coups(self, grille, lPositions):
        lScores1 = [None]*len(lPositions)
        lScores2 = [None]*len(lPositions)
        lScoresTotal = [[None]*self.nbConstantes for _ in range(len(lPositions))]
        lMax = [-float("inf") for _ in range(self.nbConstantes)]
        lMin = [float("inf") for _ in range(self.nbConstantes)]
        for iP,(x1,y1,o1,t1,x2,y2,o2,t2) in enumerate(lPositions):
            self.jeu.mettre_dans_grille(grille, x1, y1, o1, t1, self.jeu.dicoCouleursPieces[t1], coin=False)
            lScores1[iP] = self.calculer_score(grille, x1, y1, o1, t1)
            self.jeu.mettre_dans_grille(grille, x2, y2, o2, t2, self.jeu.dicoCouleursPieces[t2], coin=False)
            lScores2[iP] = self.calculer_score(grille, x2, y2, o2, t2)
            self.jeu.enlever_de_grille(grille, x1, y1, o1, t1, None, coin=False)
            self.jeu.enlever_de_grille(grille, x2, y2, o2, t2, None, coin=False)
            for i in range(self.nbConstantes):
                score1 = lScores1[iP][i] if lScores1[iP][i] is not None else 0
                score2 = lScores2[iP][i] if lScores2[iP][i] is not None else 0
                lScoresTotal[iP][i] = score1+score2
                lMax[i] = max(lMax[i], score1+score2)
                lMin[i] = min(lMin[i], score1+score2)

        scoreMax = -float("inf")
        meilleurePosition = (None,None,None,None) #(x,y,o,t)
        for iP,position in enumerate(lPositions):
            score = 0
            for i in range(self.nbConstantes):
                ecart = lMax[i]-lMin[i]
                if ecart < 1e-10:
                    valeur = 0
                else :
                    valeur = (lScoresTotal[iP][i]-lMin[i]) / ecart
                score += valeur*self.lConstantes[i]
            if score > scoreMax :
                scoreMax = score
                meilleurePosition = position
        return meilleurePosition, scoreMax

    def calculer_meilleure_position_1_coup(self, grille, lPositions):
        lScores = [None]*len(lPositions)
        lMax = [-float("inf") for _ in range(self.nbConstantes)]
        lMin = [float("inf") for _ in range(self.nbConstantes)]
        for iP,(x, y, o, t) in enumerate(lPositions):
            self.jeu.mettre_dans_grille(grille, x, y, o, t, self.jeu.dicoCouleursPieces[t], coin=False)
            lScores[iP] = self.calculer_score(grille, x, y, o, t)
            self.jeu.enlever_de_grille(grille, x, y, o, t, None, coin=False)
            for i in range(self.nbConstantes):
                score = lScores[iP][i] if lScores[iP][i] is not None else 0
                lScores[iP][i] = score
                lMax[i] = max(lMax[i], score)
                lMin[i] = min(lMin[i], score)

        scoreMax = -float("inf")
        meilleurePosition = (None,None,None,None) #(x,y,o,t)
        for iP,position in enumerate(lPositions):
            score = 0
            for i in range(self.nbConstantes):
                ecart = lMax[i]-lMin[i]
                if ecart < 1e-10:
                    valeur = 0
                else :
                    valeur = (lScores[iP][i]-lMin[i]) / ecart
                score += valeur*self.lConstantes[i]
            if score > scoreMax :
                scoreMax = score
                meilleurePosition = position
        return meilleurePosition, scoreMax

    def calculer_score(self, grille, x, y, o, t):
        score = [None]*self.nbConstantes
        score[0] = -self.hauteur_max_grille(grille)
        score[1] = -self.hauteur_max_piece(x, y, o, t)
        score[2] = -self.somme_hauteurs_grille(grille)
        score[3] = -self.nb_trous_normal(grille)
        score[4] = -self.irregularites(grille)
        score[5] = self.nb_lignes(grille)
        return score

    def appliquer_position(self):
        if self.nbCoups == 1:
            self.lPositionsPieces = self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.piece)
            self.jouer_1_coup(self.jeu.grille, self.lPositionsPieces, self.jeu.piece)
        elif self.nbCoups == 2 :
            self.jeu.nextPiece.reset()
            self.lPositionsPieces = self.calculer_toutes_positions_2_coups(self.jeu.grille, self.jeu.piece, self.jeu.nextPiece)
            self.jouer_2_coups(self.jeu.grille, self.lPositionsPieces, self.jeu.piece, self.jeu.nextPiece)
        elif self.nbCoups == 3 :
            if self.jeu.holdPiece is None:
                self.jeu.mettre_piece_hold()
            self.jeu.holdPiece.reset()
            self.lPositionsPieces = [self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.piece), self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.holdPiece)]
            self.joueur_3_coups(self.jeu.grille, self.lPositionsPieces, self.jeu.piece, self.jeu.holdPiece)

    def appliquer_position_2_coups(self, grille, piece1, position1, piece2, position2):
        #Piece 1
        x1,y1,o1,t1 = position1
        piece1.x = x1
        piece1.y = y1
        piece1.orientation = o1
        piece1.type = t1
        piece1.matrice = self.jeu.dicoMatricesPieces[(t1,o1)]
        piece1.fixer(tester_lignes=False)
        #Piece 2
        x2,y2,o2,t2 = position2
        piece2.x = x2
        piece2.y = y2
        piece2.orientation = o2
        piece2.type = t2
        piece2.matrice = self.jeu.dicoMatricesPieces[(t2,o2)]
        piece2.fixer()

    def appliquer_position_1_coup(self, grille, piece, position):
        x,y,o,t = position
        piece.x = x
        piece.y = y
        piece.orientation = o
        piece.type = t
        piece.matrice = self.jeu.dicoMatricesPieces[(t,o)]
        piece.fixer()

    def jouer_1_coup(self, grille, lPositionsPieces, piece):
        meilleurePosition, meilleurScore = self.calculer_meilleure_position_1_coup(grille, lPositionsPieces)
        if any([arg is None for arg in meilleurePosition]):
            self.jeu.finJeu = True
            return
        self.appliquer_position_1_coup(grille, piece, meilleurePosition)

    def jouer_2_coups(self, grille, lPositionsPieces, piece1, piece2):
        meilleurePosition, meilleurScore = self.calculer_meilleure_position_2_coups(grille, lPositionsPieces)
        if any([arg is None for arg in meilleurePosition]):
            self.jeu.finJeu = True
            return
        self.appliquer_position_2_coups(grille, piece1, meilleurePosition[:4], piece2, meilleurePosition[4:])

    def joueur_3_coups(self, grille, lPositionsPieces, piece, holdPiece):
        meilleurePositionPiece, scorePiece = self.calculer_meilleure_position_1_coup(grille, lPositionsPieces[0])
        meilleurePositionHold, scoreHold = self.calculer_meilleure_position_1_coup(grille, lPositionsPieces[1])
        if scorePiece >= scoreHold:
            if any([arg is None for arg in meilleurePositionPiece]):
                self.jeu.finJeu = True
                return
            self.appliquer_position_1_coup(grille, piece, meilleurePositionPiece)
        else :
            if any([arg is None for arg in meilleurePositionHold]):
                self.jeu.finJeu = True
                return
            self.jeu.mettre_piece_hold()
            self.appliquer_position_1_coup(grille, holdPiece, meilleurePositionHold)

    def boucle_jeu(self):
        if not self.jeu.modeAlgo :
            return
        if self.dtAlgo > 0 and self.tAlgo+self.dtAlgo > pygame.time.get_ticks() :
            return
        self.tAlgo = pygame.time.get_ticks()
        self.appliquer_position()
        #self.jeu.tester_clavier_appuie(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))

    def changer_nb_coups(self, ajout):
        self.nbCoups = (self.nbCoups-1+ajout) % self.nbCoupsMax + 1
        self.jeu.texteNbCoupsAlgo = self.jeu.police.render(f"NbCoups Algo : {self.nbCoups}", False, self.jeu.couleurTextes)

    def afficher_toutes_positions(self):
        if not self.visuelPositions:
            return
        if self.nbCoups == 1:
            if self.iPosition >= len(self.lPositionsPieces):
                self.changer_visuel_positions()
                return
            x,y,o,t = self.lPositionsPieces[self.iPosition]
            self.jeu.mettre_dans_grille(self.jeu.grille, x, y, o, t, (0,0,0), coin=False)
        elif self.nbCoups == 2:
            if self.iPosition >= len(self.lPositionsPieces):
                self.changer_visuel_positions()
                return
            x1,y1,o1,t1,x2,y2,o2,t2 = self.lPositionsPieces[self.iPosition]
            self.jeu.mettre_dans_grille(self.jeu.grille, x1, y1, o1, t1, (0,0,0), coin=False)
            self.jeu.mettre_dans_grille(self.jeu.grille, x2, y2, o2, t2, (0,0,0), coin=False)
        elif self.nbCoups == 3:
            if self.iPosition >= len(self.lPositionsPieces[0])+len(self.lPositionsPieces[1]):
                self.changer_visuel_positions()
                return
            elif self.iPosition < len(self.lPositionsPieces[0]):
                x,y,o,t = self.lPositionsPieces[0][self.iPosition]
            else :
                x,y,o,t = self.lPositionsPieces[1][self.iPosition-len(self.lPositionsPieces[0])]
            self.jeu.mettre_dans_grille(self.jeu.grille, x, y, o, t, (0,0,0), coin=False)

    def desafficher_toutes_positions(self):
        if not self.visuelPositions:
            return
        if self.nbCoups == 1:
            x,y,o,t = self.lPositionsPieces[self.iPosition]
            self.jeu.enlever_de_grille(self.jeu.grille, x, y, o, t, (0,0,0), coin=False)
        elif self.nbCoups == 2:
            x1,y1,o1,t1,x2,y2,o2,t2 = self.lPositionsPieces[self.iPosition]
            self.jeu.enlever_de_grille(self.jeu.grille, x1, y1, o1, t1, (0,0,0), coin=False)
            self.jeu.enlever_de_grille(self.jeu.grille, x2, y2, o2, t2, (0,0,0), coin=False)
        elif self.nbCoups == 3:
            if self.iPosition < len(self.lPositionsPieces[0]):
                x,y,o,t = self.lPositionsPieces[0][self.iPosition]
            else :
                x,y,o,t = self.lPositionsPieces[1][self.iPosition-len(self.lPositionsPieces[0])]
            self.jeu.enlever_de_grille(self.jeu.grille, x, y, o, t, (0,0,0), coin=False)
        if pygame.time.get_ticks() >= self.tPositionsAvant + self.dtPositionsInit:
            self.tPositionsAvant = pygame.time.get_ticks()
            self.iPosition += 1

    def changer_visuel_positions(self):
        if self.visuelPositions:
            self.jeu.piece.bouge = True
            self.jeu.piece.tempsAvant = pygame.time.get_ticks()
        else :
            self.jeu.piece.bouge = False
            self.iPosition = 0
            self.tPositionsAvant = pygame.time.get_ticks()
        self.visuelPositions = not self.visuelPositions



"""Faire max(score1 + max(score2)) pour chaque score1"""