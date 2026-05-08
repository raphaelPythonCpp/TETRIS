import pygame
from collections import deque
import numpy as np

class Menus(object):
    def __init__(self, jeu, lAttributsPolice, horloge):
        self.jeu = jeu
        self.horloge = horloge

        self.actif = False

        dicoNomsFichiersChiffres = {**{str(i) : f"{i}.png" for i in range(10)}, **{chr(65+i) : f"{chr(65+i)}.png" for i in range(26)}, '.' : "point.png", ',' : "virgule.png", ' ' : "espace.png", '-' : "moins.png"}
        self.generateurTexte = Generateur_Texte(self, lAttributsPolice, "MENUS\\IMAGES_BASE", "CARACTERES_TEXTE", "MENUS\\IMAGES_UTILES", dicoNomsFichiersChiffres, transparence=True, enregistrement=False)
        self.modeTexte = "POLICE" #ou "IMAGES"

        self.wBoutons = 50
        self.lPositionsBoutons = [(5+i*1.1*self.wBoutons, 5) for i in range(10)]

        self.menuDidactique = Menu_didactique(self, self.jeu, ["hauteur max grille", "hauteur max piece", "somme hauteurs", "nb trous normaux", "score irregularites", "nb lignes", "score puits"], 50, avecTorch=self.jeu.algorithme) #ATTENTION : pas le bon nom de fichier
        self.menuHome = Menu_home(self, self.jeu)
        self.menuGameOver = Menu_Game_Over(self, self.jeu)

        self.lMenus = [self.menuHome, self.menuDidactique, self.menuGameOver]

    def boucle(self):
        self.actif = True
        while self.actif :
            self.horloge.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.jeu.quitterProgramme = True
                    self.actif = False
                    break
            self.gerer_souris()
            self.afficher()
        self.jeu.modeGrille = self.menuHome.lNiveaux.index(self.menuHome.niveau)
        self.jeu.changer_grille()

    def afficher(self):
        self.jeu.fenetre.fill((0,0,0))

        for menu in self.lMenus:
            if menu.actif :
                menu.afficher()

        pygame.display.flip()

    def gerer_souris(self):
        for menu in self.lMenus:
            if menu.actif :
                menu.gerer_souris()

    def modifier_dimensions(self, image, w=None, h=None):
        wI, hI = image.get_size()
        facteur = 1 if (w is None and h is None) else min(w/wI, h/hI) if (w is not None and h is not None) else w/wI if (w is not None) else h/hI
        dimensions2 = (int(wI * facteur), int(hI * facteur))
        image2 = pygame.transform.smoothscale(image, dimensions2)
        return image2, dimensions2

    def ouvrir_image(self, dossier1, dossier2, nom, dossier3=None, w=None, h=None, transparence=False, enregistrement=False):
        chemin = f"{dossier1}\\{dossier2}\\{nom}"
        image = pygame.image.load(chemin).convert_alpha() if transparence else pygame.image.load(chemin).convert()
        image, dimensions = self.modifier_dimensions(image, w, h)
        if enregistrement:
            pygame.image.save(image, f"{dossier1}\\{dossier3}\\{nom}")
        return image, dimensions

    def extraire_tous_boutons(self, dossier1, dossier2, dossier3, nom, lNomsBoutons):
        imageAsset, (wA, hA) = self.ouvrir_image(dossier1, dossier2, nom, dossier3=None, h=None, transparence=True, enregistrement=False)
        vu = [[imageAsset.get_at((x,y))[3] == 0 for x in range(wA)] for y in range(hA)]
        lDXY = [(x,y) for x in range(-1,2) for y in range(-1,2) if x != 0 or y != 0]
        lRectangles = []
        for Y in range(hA):
            for X in range(wA):
                if vu[Y][X]:
                    continue
                vu[Y][X] = True
                file = deque([(X,Y)])
                xMin,xMax,yMin,yMax = X,X,Y,Y
                while file:
                    x,y = file.popleft()
                    for dx,dy in lDXY:
                        x2, y2 = x+dx, y+dy
                        if (0 <= x2 < wA) and (0 <= y2 < hA) and not vu[y2][x2]:
                            vu[y2][x2] = True
                            file.append((x2,y2))
                            xMin = min(xMin, x2)
                            xMax = max(xMax, x2)
                            yMin = min(yMin, y2)
                            yMax = max(yMax, y2)
                lRectangles.append((xMin, yMin, xMax-xMin+1, yMax-yMin+1))
        for rectangle, nomBouton in zip(lRectangles, lNomsBoutons):
            bouton = imageAsset.subsurface(rectangle).copy()
            pygame.image.save(bouton, f"{dossier1}\\{dossier3}\\{nomBouton}.png")

    def changer_couleur(self, image, facteur):
        image2 = image.copy()
        rgb = pygame.surfarray.pixels3d(image2)
        #alpha = pygame.surfarray.pixels_alpha(image2)
        rgb[:] = np.clip(rgb * facteur, 0, 255)
        return image2




class Menu_home(object):
    def __init__(self, menus, jeu):
        self.menus = menus
        self.jeu = jeu

        self.actif = False

        self.dossier = "MENUS"
        self.dossierImagesBase = "IMAGES_BASE"
        self.dossierImages = "IMAGES_UTILES"

        self.imFond = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "background_1.jpg", None, self.jeu.fenetre.get_height(), (0, 0), False, True)
        self.imFond.image.set_alpha(80)
        self.boutonQuitter = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "quitter_1.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0], True, False)
        self.boutonJouer2 = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "jouer.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1], True, False)
        self.boutonMenuDidactique = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "journal.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[2], True, False)
        
        wBoutonsNiveau = 120
        xInitBoutonsNiveau = self.jeu.wF/2 - 3/2*1.1*wBoutonsNiveau
        lPositionsBoutonsNiveau = [(xInitBoutonsNiveau+i*1.1*wBoutonsNiveau, 470) for i in range(3)]
        lPositionsImFormeNiveau = [(xBN, yBN + wBoutonsNiveau/2) for xBN, yBN in lPositionsBoutonsNiveau]
        self.boutonEasy = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "easy.png", wBoutonsNiveau, None, lPositionsBoutonsNiveau[0], True, False)
        self.imFormeEasy = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "easy_forme.png", wBoutonsNiveau, None, lPositionsImFormeNiveau[0], True, False)
        self.imGrilleEasy = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "grille_I_blanc.png", wBoutonsNiveau, None, None, True, False)
        self.imGrilleEasy.position = (lPositionsBoutonsNiveau[0][0], lPositionsBoutonsNiveau[0][1]-60-self.imGrilleEasy.dimensions[1]/2)
        self.boutonMedium = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "medium.png", wBoutonsNiveau, None, lPositionsBoutonsNiveau[1], True, False)
        self.imFormeMedium = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "medium_forme.png", wBoutonsNiveau, None, lPositionsImFormeNiveau[1], True, False)
        self.imGrilleMedium = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "grille_T_blanc.png", wBoutonsNiveau, None, None, True, False)
        self.imGrilleMedium.position = (lPositionsBoutonsNiveau[1][0], lPositionsBoutonsNiveau[1][1]-60-self.imGrilleMedium.dimensions[1]/2)
        self.boutonHard = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "hard.png", wBoutonsNiveau, None, lPositionsBoutonsNiveau[2], True, False)
        self.imFormeHard = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "hard_forme.png", wBoutonsNiveau, None, lPositionsImFormeNiveau[2], True, False)
        self.imGrilleHard = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "grille_X_blanc.png", wBoutonsNiveau, None, None, True, False)
        self.imGrilleHard.position = (lPositionsBoutonsNiveau[2][0], lPositionsBoutonsNiveau[2][1]-60-self.imGrilleHard.dimensions[1]/2)

        self.lNiveaux = [("Easy", self.imFormeEasy), ("Medium", self.imFormeMedium), ("Hard", self.imFormeHard)]
        self.niveau = self.lNiveaux[0]

        self.boutonJouer = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "logo_1.png", None, 0.5*self.jeu.hF, None, True, False)
        self.boutonJouer.image.position = (self.jeu.wF/2 - self.boutonJouer.image.dimensions[0]/2, 30)
        #self.boutonJouer = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "jouer_tetris.png", 200, None, (300, 440), True, False)
        #self.texteNiveau = self.menus.generateurTexte.creer_surface_texte(f"{self.scoreMoyen:.2f}", 0.3*self.jeu.wF, self.jeu.hF, 0.05, self.couleurTexte)
        #self.boutonReset = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "changer.png", *self.menus.tailleBoutons, (105,5), True, False)


        self.lImages = [self.imFond, self.imGrilleEasy, self.imGrilleMedium, self.imGrilleHard]
        self.lBoutons = [self.boutonEcriture, self.boutonMenuDidactique, self.boutonEasy, self.boutonMedium, self.boutonHard, self.boutonJouer]
        self.lElements = self.lImages + self.lBoutons

    def afficher(self):
        for element in self.lElements:
            element.afficher(self.jeu.fenetre)
        self.niveau[1].afficher(self.jeu.fenetre)

        lTouchesPressees = pygame.key.get_pressed()
        if self.boutonQuitter.hover and not lTouchesPressees[pygame.K_q] :
            self.boutonJouer2.afficher(self.jeu.fenetre)
        else :
            self.boutonQuitter.afficher(self.jeu.fenetre)

    def gerer_souris(self):
        lTouchesPressees = pygame.key.get_pressed()
        if self.boutonQuitter.gerer_souris() and lTouchesPressees[pygame.K_q]:
            self.actif = False
            self.menus.actif = False
            self.jeu.quitterProgramme = True
        if self.boutonJouer2.gerer_souris() and not lTouchesPressees[pygame.K_q]:
            self.actif = False
            self.menus.actif = False
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
        if self.boutonMenuDidactique.gerer_souris():
            self.actif = False
            self.menus.menuDidactique.actif = True
        if self.boutonEasy.gerer_souris():
            self.niveau = self.lNiveaux[0]
        if self.boutonMedium.gerer_souris():
            self.niveau = self.lNiveaux[1]
        if self.boutonHard.gerer_souris():
            self.niveau = self.lNiveaux[2]
        if self.boutonJouer.gerer_souris():
            self.actif = False
            self.menus.actif = False





class Menu_Game_Over(object):
    def __init__(self, menus, jeu):
        self.menus = menus
        self.jeu = jeu

        self.actif = False

        self.dossier = "MENUS"
        self.dossierImagesBase = "IMAGES_BASE"
        self.dossierImages = "IMAGES_UTILES"

        self.imFond = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "background_1.jpg", None, self.jeu.fenetre.get_height(), (0, 0), False, True)
        self.imFond.image.set_alpha(80)
        self.boutonHome = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0], True, False)
        self.imGameOver = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "game_over_2.png", self.jeu.wF, None, None, False, True)
        self.imGameOver.position = (0, self.jeu.hF - self.imGameOver.dimensions[1])

        self.lImages = [self.imFond, self.imGameOver]
        self.lBoutons = [self.boutonHome]
        self.lElements = self.lImages + self.lBoutons

    def afficher(self):
        for element in self.lElements:
            element.afficher(self.jeu.fenetre)

    def gerer_souris(self):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True






class Menu_didactique(object):
    def __init__(self, menus, jeu, lNomsConstantes, nbParties, avecTorch):
        self.jeu = jeu
        self.menus = menus

        self.actif = False

        self.lNomsConstantes = lNomsConstantes
        self.nbConstantes = len(self.lNomsConstantes)

        self.dossier = "MENUS"
        self.dossierImagesBase = "IMAGES_BASE"
        self.dossierImages = "IMAGES_UTILES"

        #charger toutes les images
        self.imFond = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "background_1.jpg", None, self.jeu.fenetre.get_height(), (0, 0), False, True)
        self.imFond.image.set_alpha(80)
        self.texteApprentissage = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\TEXTES", self.dossierImages, "texte_apprentissage.png", None, 0.08*self.jeu.hF, None, True, False)
        self.texteApprentissage.position = ((self.jeu.wF-self.texteApprentissage.dimensions[0])/2, 0.01*self.jeu.hF)
        self.boutonHome = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1], True, False)
        self.boutonReset = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "changer.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[2], True, False)
        self.boutonPrediction = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\TEXTES", self.dossierImages, "texte_prediction.png", 0.4*self.jeu.wF, None, None, True, False)
        self.boutonPrediction.image.position = (0.55*self.jeu.wF, 0.1*self.jeu.hF)

        self.lImages = [self.imFond, self.texteApprentissage]
        self.lBoutons = [self.boutonHome, self.boutonEcriture, self.boutonReset, self.boutonPrediction]

        aFondSliders = 180
        cMinFondSliders, cMaxFondSliders = 70, 200
        self.couleurTexte = (255, 255, 255)#(cMaxFondSliders/2, cMaxFondSliders/2, cMaxFondSliders/2)
        wTexteSliders, hTexteSliders, espacementTexteSliders = 0.35, 0.4, 0.05
        lCouleursSliders = [("rouge", "rouge", (cMaxFondSliders,0,0,aFondSliders), (cMinFondSliders,0,0)), ("vert", "verte", (0,cMaxFondSliders,0,aFondSliders), (0,cMinFondSliders,0)), ("bleu", "bleue", (0,0,cMaxFondSliders,aFondSliders), (0,0,cMinFondSliders)), ("jaune", "jaune", (cMaxFondSliders,cMaxFondSliders,0,aFondSliders), (cMinFondSliders,cMinFondSliders,0)), ("violet", "violette", (cMaxFondSliders,0,cMaxFondSliders,aFondSliders), (cMinFondSliders,0,cMinFondSliders)), ("orange", "orange", (cMaxFondSliders,(cMinFondSliders*0.7+0.3*cMaxFondSliders),0,aFondSliders), (cMinFondSliders,cMinFondSliders//2,0)), ("cyan", "cyan", (0,cMaxFondSliders,cMaxFondSliders,aFondSliders), (0,cMinFondSliders,cMinFondSliders))]
        lCarSliders = [(nom, "cadre_barre_11.png", "carre_noir.png", f"carre_{couleur1}.png", f"forme_{couleur2}.png", rgbaFond, rgbTexte) for nom, (couleur1, couleur2, rgbaFond, rgbTexte) in zip(lNomsConstantes, lCouleursSliders)]
        yMinSliders = 0.1*self.jeu.hF#self.boutonPrediction.image.dimensions[1]*1.15
        hSlider = (self.jeu.hF - yMinSliders) / len(lNomsConstantes)
        assert len(lNomsConstantes) <= len(lCouleursSliders), "Plus de constantes que de couleurs disponibles"
        self.lSliders = []
        for iS, (nom,nomCadre,nomCarreNoir,nomCarreColore,nomForme,couleurFond,couleurTexte) in enumerate(lCarSliders):
            self.lSliders.append(Slider(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ELEMENTS_SLIDERS", self.dossierImages, nom, nomCadre, nomCarreNoir, nomCarreColore, nomForme, (0.03*self.jeu.wF, yMinSliders+iS*hSlider, 0.5*self.jeu.wF, 0.9*hSlider), (wTexteSliders, hTexteSliders, espacementTexteSliders), True, -1, 1, 13, None, couleurFond, self.couleurTexte, True))
        self.sliderProgressionEvaluation = Slider(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ELEMENTS_SLIDERS", self.dossierImages, "Progression Evaluation", "cadre_barre_11.png", "carre_rouge.png", "carre_vert.png", "forme_jaune.png", (0.55*self.jeu.wF, 0.2*self.jeu.hF, 0.43*self.jeu.wF, 0.5*hSlider), (wTexteSliders, hTexteSliders, espacementTexteSliders), True, 0, 100, 20, 0, (cMaxFondSliders/2, cMaxFondSliders/2, cMaxFondSliders/2, aFondSliders), self.couleurTexte, False)
        self.lSliders.append(self.sliderProgressionEvaluation)

        self.lElements = self.lImages + self.lBoutons + self.lSliders


        self.avecTorch = avecTorch
        if self.avecTorch:
            global torch
            import torch
        self.lNbNoeuds = [self.nbConstantes, 1]
        if self.jeu.algorithme:
            self.modele = self.jeu.algo.creer_reseau(self.lNbNoeuds)
        self.nbParties = nbParties
        self.scoreMoyen, self.nbCoupsMoyen = 0,0
        self.changer_resultats()

    def afficher(self):
        for element in self.lElements:
            element.afficher(self.jeu.fenetre)
        self.jeu.fenetre.blit(self.texteScoreMoyen, self.positionTexteScoreMoyen)
        self.jeu.fenetre.blit(self.texteNbCoupsMoyen, self.positionTexteNbCoupsMoyen)

    def evaluation(self):
        if not self.avecTorch:
            print("Pas possible sans activer Torch")
            return
        lValeurs = [slider.valeur for slider in self.lSliders[:self.nbConstantes]]
        dicoReseau = {'0.weight' : torch.tensor(lValeurs, dtype=torch.float32).unsqueeze(0), '0.bias' : torch.zeros(1, dtype=torch.float32)}
        self.modele.load_state_dict(dicoReseau)
        self.scoreMoyen, self.nbCoupsMoyen = self.jeu.algo.evaluation_algo(self.nbParties, self.modele, affichage=True, visuel=False, fonctionAvancement=self.lSliders[self.nbConstantes].changer_valeur)
        self.changer_resultats()

    def gerer_souris(self):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            for slider in self.lSliders:
                slider.changer_mode_texte()
            self.changer_resultats()
        if self.boutonReset.gerer_souris():
            for slider in self.lSliders[:-1]:
                slider.iValeur = slider.nbValeurs // 2
                slider.maj_valeur()
        if self.boutonPrediction.gerer_souris():
            self.evaluation()
        for slider in self.lSliders:
            slider.gerer_souris()

    def changer_resultats(self):
        self.texteScoreMoyen = self.menus.generateurTexte.creer_surface_texte(f"{self.scoreMoyen:.2f}", 0.3*self.jeu.wF, self.jeu.hF, 0.05, self.couleurTexte)
        self.positionTexteScoreMoyen = (0.6*self.jeu.wF, 0.3*self.jeu.hF)
        self.texteNbCoupsMoyen = self.menus.generateurTexte.creer_surface_texte(f"{self.nbCoupsMoyen:.2f}", 0.3*self.jeu.wF, self.jeu.hF, 0.05, self.couleurTexte)
        self.positionTexteNbCoupsMoyen = (0.6*self.jeu.wF, 0.45*self.jeu.hF)









class Slider(object):
    def __init__(self, menus, menu, dossier1, dossier2, dossier3, nom, nomCadre, nomCarreNoir, nomCarreColore, nomForme, rectangleFond, caracteristiquesTexte, enregistrement, valeurMin, valeurMax, nbValeurs, iValeur, couleurFond, couleurTexte, interactif):
        self.menus = menus
        self.menu = menu
        self.interactif = interactif

        self.hover = False
        self.couleurFond = couleurFond
        self.xFond, self.yFond, self.wFond, self.hFond = rectangleFond
        self.fond = pygame.Surface((self.wFond, self.hFond), pygame.SRCALPHA)
        self.borderRadiusFond = round(min(self.fond.get_size())*0.3)

        self.imCadre = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nomCadre, w=None, h=None, position=(0.15*self.wFond + caracteristiquesTexte[0]*self.wFond, 0.55*self.hFond), transparence=False, enregistrement=enregistrement)
        self.wCarres = round(0.4*self.wFond / (nbValeurs-1+0.32))
        self.imCadre.dimensions = (round(0.4*self.wFond), round(1.21*self.wCarres))
        self.imCadre.image = pygame.transform.smoothscale(self.imCadre.image, self.imCadre.dimensions)
        hCarres = round(0.78*self.imCadre.dimensions[1])
        self.wCarres = round(hCarres*1.075)
        self.imCarreNoir = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nomCarreNoir, None, hCarres, None, False, enregistrement)
        self.imCarreColore = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nomCarreColore, None, hCarres, None, False, enregistrement)
        hForme = round(0.7*hCarres)
        self.imForme = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nomForme, None, hForme, None, True, enregistrement)
        self.xDebutCarres = round(self.imCadre.position[0] + 0.24*hCarres)
        self.yDebutCarres = round(self.imCadre.position[1] + 0.13*hCarres)

        self.nbValeurs = nbValeurs
        self.iValeur = self.nbValeurs//2 if iValeur is None else iValeur
        self.valeurMin, self.valeurMax = valeurMin, valeurMax
        self.deltaValeur = (self.valeurMax - self.valeurMin) / (self.nbValeurs-1)
        self.lValeurs = [float(f"{self.valeurMin+i*self.deltaValeur:.2f}") for i in range(self.nbValeurs)]
        self.valeur = self.lValeurs[self.iValeur]
        self.lPositionsCarres = [(self.xDebutCarres+i*self.wCarres, self.yDebutCarres) for i in range(self.nbValeurs)]
        self.lPositionsForme = [(xC-self.imForme.dimensions[0]/2-(self.wCarres-self.imCarreNoir.dimensions[0])/2, yC+0.5*(hCarres-self.imForme.dimensions[1])) for i,(xC,yC) in enumerate(self.lPositionsCarres)]
        self.lPositionsCarres.pop()

        self.couleurTexte = couleurTexte
        self.nom = nom
        self.caracteristiquesTexte = caracteristiquesTexte
        self.changer_mode_texte()

        self.bouge = False
        self.xSA, self.ySA = None,None

    def afficher(self, fenetre):
        self.fond.fill((0,0,0,0))
        couleurFond = tuple(map(lambda x : min(255, round(x*1.5)), (self.couleurFond))) if self.hover else self.couleurFond
        pygame.draw.rect(self.fond, couleurFond, self.fond.get_rect())#, border_radius=self.borderRadiusFond)
        couleurBordFond = tuple(map(lambda x : min(255, round(x*0.5)), (couleurFond[:3]))) + (couleurFond[3],) if self.bouge else couleurFond
        pygame.draw.rect(self.fond, couleurBordFond, self.fond.get_rect())#, border_radius=self.borderRadiusFond, width=round(self.hFond/15))
        #Barre
        self.imCadre.afficher(self.fond)
        for iV in range(self.nbValeurs-1):
            if iV < self.iValeur:
                self.imCarreColore.afficher(self.fond, self.lPositionsCarres[iV])
            else :
                self.imCarreNoir.afficher(self.fond, self.lPositionsCarres[iV])
        if self.interactif:
            if self.bouge:
                self.imForme.afficher(self.fond, (max(self.lPositionsForme[0][0], min(self.lPositionsForme[-1][0], self.xSA-self.imForme.dimensions[0]/2)), self.lPositionsForme[self.iValeur][1]))
            else :
                self.imForme.afficher(self.fond, self.lPositionsForme[self.iValeur])
        #Textes
        self.fond.blit(self.texteValeurMin, self.positionTexteVMin)
        self.fond.blit(self.texteValeurMax, self.positionTexteVMax)
        self.fond.blit(self.texteValeur, self.positionTexteV)
        self.fond.blit(self.texteNom, self.positionTexteNom)

        fenetre.blit(self.fond, (self.xFond, self.yFond))

    def changer_mode_texte(self):
        self.maj_valeur_min()
        self.maj_valeur_max()
        self.maj_valeur()
        self.maj_nom()

    def gerer_souris(self):
        xS,yS = pygame.mouse.get_pos()
        xS -= self.xFond
        yS -= self.yFond
        self.hover = (0 <= xS <= self.wFond) and (0 <= yS <= self.hFond)
        if self.bouge:
            if not pygame.mouse.get_pressed()[0]:
                self.bouge = False
                self.imForme.position = self.lPositionsForme[self.iValeur]
                self.xSA, self.ySA = None,None
            elif self.interactif:
                if self.iValeur > 0 and xS <= self.lPositionsCarres[self.iValeur-1][0]:
                    self.iValeur -= 1
                    self.maj_valeur()
                elif self.iValeur+1 < self.nbValeurs and xS > self.lPositionsCarres[self.iValeur][0]+self.wCarres:
                    self.iValeur += 1
                    self.maj_valeur()
                self.xSA, self.ySA = xS, yS
        elif self.interactif and pygame.mouse.get_pressed()[0] and self.imForme.tester_hover(xS, yS):
            self.bouge = True
            self.xSA, self.ySA = xS, yS

    def changer_valeur(self, valeur):
        iValeur = max(i if v<=valeur else -1 for i,v in enumerate(self.lValeurs))
        if iValeur != self.iValeur:
            self.iValeur = iValeur
            self.maj_valeur()
            self.menu.afficher()

    def maj_valeur(self):
        self.valeur = self.lValeurs[self.iValeur]
        self.texteValeur = self.menus.generateurTexte.creer_surface_texte(str(self.valeur), 0.2*self.wFond, 0.3*self.hFond, 0.1, self.couleurTexte)
        self.positionTexteV = (self.imCadre.position[0]+(self.imCadre.dimensions[0]-self.texteValeur.get_width())/2, self.imCadre.position[1]-self.texteValeur.get_height()-0.05*self.hFond)

    def maj_valeur_min(self):
        self.texteValeurMin = self.menus.generateurTexte.creer_surface_texte(str(self.valeurMin), 0.2*self.wFond, 0.3*self.hFond, 0.05, self.couleurTexte)
        self.positionTexteVMin = (self.imCadre.position[0]-(self.texteValeurMin.get_width()+self.imCarreNoir.image.get_width()/2), self.imCadre.position[1]+(self.imCadre.dimensions[1]-self.texteValeurMin.get_height())/2)

    def maj_valeur_max(self):
        self.texteValeurMax = self.menus.generateurTexte.creer_surface_texte(str(self.valeurMax), 0.2*self.wFond, 0.3*self.hFond, 0.05, self.couleurTexte)
        self.positionTexteVMax = (self.imCadre.position[0]+self.imCadre.dimensions[0]+self.imCarreNoir.image.get_width()/2, self.imCadre.position[1]+(self.imCadre.dimensions[1]-self.texteValeurMax.get_height())/2)

    def maj_nom(self):
        wT, hT, eT = self.caracteristiquesTexte
        wTexte = wT*self.wFond
        hTexte = hT*self.hFond
        self.texteNom = self.menus.generateurTexte.creer_surface_texte(self.nom, wTexte, hTexte, eT, self.couleurTexte)
        self.positionTexteNom = (0.03*self.wFond + (wTexte-self.texteNom.get_width())/2, self.imCadre.position[1])#(self.hFond-self.texteNom.get_height())/2)










class Generateur_Texte(object):
    def __init__(self, menus, lAttributsPolice, dossier1, dossier2, dossier3, dicoNoms, transparence, enregistrement):
        self.menus = menus #class Menus

        self.lImages = {nom : Image(self.menus, self, dossier1, dossier2, dossier3, nomFichier, None, None, None, transparence, enregistrement) for nom,nomFichier in dicoNoms.items()}
        self.dicoImagesVu = {}
        self.nomPolice, self.taillePolice, self.grasPolice, self.italiquePolice = lAttributsPolice
        self.dicoPoliceVues = {}

    def recuperer_image(self, nom, w, h):
        dico = self.dicoImagesVu if self.menus.modeTexte == "IMAGES" else self.dicoPoliceVues
        if self.menus.modeTexte == "IMAGES":
            cle = (nom, w, h)
            if cle not in dico:
                image, _ = self.menus.modifier_dimensions(self.lImages[nom].image, w, h)
                dico[cle] = image
            return dico[cle]
        elif self.menus.modeTexte == "POLICE":
            cle = round(h)
            if cle not in dico:
                police = pygame.font.SysFont(self.nomPolice, cle, bold=self.grasPolice, italic=self.italiquePolice)
                #print(f"hTheorique = {cle} VS hRender = {police.render('None', True, (0,0,0)).get_height()}")
                dico[cle] = police
            return dico[cle].render(nom, True, (0,0,0))

    def creer_surface_texte(self, texte, wTotal, hTotal, espacement, couleur=None):
        texte = texte.upper()
        hL, hR = 0, hTotal
        while hR-hL > 1e-2:
            hM = (hL + hR)/2
            wImagesTotal = 0
            for car in texte:
                wImagesTotal += self.recuperer_image(car, hTotal, hM).get_width()
            wEspacement = (espacement*wImagesTotal) / (len(texte)-1) if len(texte) > 1 else 0
            wTotal2 = wImagesTotal + wEspacement*(len(texte)-1)
            if wTotal2 > wTotal:
                hR = hM
            else :
                hL = hM
        hI = hL
        lImages = []
        wImagesTotal = 0
        for car in texte:
            lImages.append(self.recuperer_image(car, wTotal, hI))
            wImagesTotal += lImages[-1].get_width()
        wEspacement = (espacement*wImagesTotal) / (len(texte)-1) if len(texte) > 1 else 0
        wTotal = wImagesTotal + wEspacement*(len(texte)-1)
        if self.menus.modeTexte == "IMAGES":
            surface = pygame.Surface((wTotal, hI), pygame.SRCALPHA)
            surface.set_alpha(0)
            x = 0
            for image in lImages:
                surface.blit(image, (x, 0))
                x += image.get_width() + wEspacement
        else :
            surface = self.dicoPoliceVues[round(hI)].render(texte, True, couleur)
        return surface








class Bouton(object):
    def __init__(self, menus, menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement):
        self.menus = menus
        self.menu = menu
        self.image = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement)
        self.imageNormal = self.image.image.copy()
        self.imageHover = self.menus.changer_couleur(self.imageNormal, 1.3)
        self.imagePressed = self.menus.changer_couleur(self.imageNormal, 0.8)
        self.hover, self.pressed = False, False

    def gerer_souris(self, xS=None, yS=None, appuie=None):
        if xS is None or yS is None:
            xS, yS = pygame.mouse.get_pos()
        if appuie is None:
            appuie = pygame.mouse.get_pressed()[0]
        self.hover = (self.image.position[0] <= xS <= self.image.position[0]+self.image.dimensions[0]) and (self.image.position[1] <= yS <= self.image.position[1]+self.image.dimensions[1])
        clicked = self.hover and self.pressed and not appuie
        self.pressed = self.hover and appuie
        return clicked

    def afficher(self, fenetre):
        image = self.imagePressed if self.pressed else self.imageHover if self.hover else self.imageNormal
        x,y = self.image.position
        y += 0.05*self.image.dimensions[1] if self.pressed else 0
        fenetre.blit(image, (x,y))





class Image(object):
    def __init__(self, menus, menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement):
        self.menus = menus
        self.menu = menu
        self.image, self.dimensions = self.menus.ouvrir_image(dossier1, dossier2, nom, dossier3, w, h, transparence, enregistrement)
        self.position = position

    def afficher(self, fenetre, position=None):
        self.position = self.position if position is None else position
        fenetre.blit(self.image, self.position)

    def tester_hover(self, xS=None, yS=None):
        if xS is None or yS is None:
            xS, yS = pygame.mouse.get_pos()
        return (self.position[0] <= xS <= self.position[0]+self.dimensions[0]) and (self.position[1] <= yS <= self.position[1]+self.dimensions[1])