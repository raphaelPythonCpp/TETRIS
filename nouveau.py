class Menu_Creation_Pieces(object):
    def __init__(self, menus, jeu, nbCases):
        self.menus = menus
        self.jeu = jeu

        self.actif = False

        self.nbCases = nbCases
        self.grille = [[False]*self.nbCases for _ in range(self.nbCases)]
        self.tailleCases = min(self.jeu.wF*0.8, self.jeu.hF*0.8)/self.nbCases
        self.xMin, self.yMin = self.jeu.wF/2-self.nbCases/2*self.tailleCases, self.jeu.hF/2-self.nbCases/2*self.tailleCases
        self.xMax, self.yMax = self.jeu.wF/2+self.nbCases/2*self.tailleCases, self.jeu.hF/2+self.nbCases/2*self.tailleCases

        self.dossier = "MENUS"
        self.dossierImagesBase = "IMAGES_BASE"
        self.dossierImages = "IMAGES_UTILES"

        self.imFond = Image(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\IMAGES", self.dossierImages, "background_1.jpg", None, self.jeu.fenetre.get_height(), (0, 0), False, True)
        self.imFond.image.set_alpha(80)
        self.boutonHome = Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0], True, False)
        self.boutonSauvegarder =Bouton(self.menus, self, self.dossier, f"{self.dossierImagesBase}\\ICONS", self.dossierImages, "sauvegarder.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1], True, False)

        self.lImages = [self.imFond]
        self.lBoutons = [self.boutonHome]
        self.lElements = self.lImages + self.lBoutons

    def afficher(self):
        for element in self.lElements:
            element.afficher(self.jeu.fenetre)
        self.jeu.afficher_grille(self.grille, self.tailleCase, self.xDebut, self.yDebut, orientation=0, piece=None, ombre=False, coin=False)

    def gerer_souris(self):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
        xS, yS = pygame.mouse.get_pos()
        if self.xMin <= xS <= self.xMax and self.yMin <= yS <= self.yMax:
            iX = (xS-self.xMin)//self.tailleCases
            iY = (yS-self.yMin)//self.tailleCases
            self.grille[iY][iX] = not self.grille[iY][iX]
