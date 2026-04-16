import pygame
from collections import deque
import numpy as np
import torch

class Menu_Parametres(object):
    def __init__(self, jeu, police, horloge):
        self.jeu = jeu
        self.police = police
        self.horloge = horloge

        self.actif = False
    
        self.dossier = "MENU_DIDACTIQUE"
        self.dossierImagesBase = "IMAGES_BASE"
        self.dossierImages = "IMAGES_UTILES"

        dicoNomsFichiersChiffres = {**{str(i) : f"{i}.png" for i in range(10)}, **{chr(65+i) : f"{chr(65+i)}.png" for i in range(26)}, '.' : "point.png", ',' : "virgule.png", ' ' : "espace.png", '-' : "moins.png"}
        self.generateurTexte = Generateur_Texte(self, self.dossier, self.dossierImagesBase, self.dossierImages, dicoNomsFichiersChiffres, transparence=True, enregistrement=False)

        #charger toutes les images
        self.imFond = Image(self, self.dossier, self.dossierImagesBase, self.dossierImages, "background_1.jpg", None, self.jeu.fenetre.get_height(), (0, 0), False, True)
        self.imFond.image.set_alpha(80)
        #self.texteApprentissage = Image(self, self.dossier, self.dossierImagesBase, self.dossierImages, "texte_apprentissage.png", None, 0.08*self.jeu.hF, None, True, False)
        #self.texteApprentissage.position = ((self.jeu.wF-self.texteApprentissage.dimensions[0])/2, 0.01*self.jeu.hF)
        self.boutonHome = Bouton(self, self.dossier, self.dossierImagesBase, self.dossierImages, "home_icon.png", None, 50, (5,5), True, False)
        self.boutonPrediction = Bouton(self, self.dossier, self.dossierImagesBase, self.dossierImages, "texte_prediction.png", 0.4*self.jeu.wF, None, None, True, False)
        self.boutonPrediction.image.position = (0.55*self.jeu.wF, 0.1*self.jeu.hF)

        aFondSliders = 180
        cMinFondSliders, cMaxFondSliders = 70, 200
        wTexteSliders, hTexteSliders, espacementTexteSliders = 0.35, 0.4, 0.05
        lCouleursSliders = [("rouge", "rouge", (cMaxFondSliders,0,0,aFondSliders), (cMinFondSliders,0,0)), ("vert", "verte", (0,cMaxFondSliders,0,aFondSliders), (0,cMinFondSliders,0)), ("bleu", "bleue", (0,0,cMaxFondSliders,aFondSliders), (0,0,cMinFondSliders)), ("jaune", "jaune", (cMaxFondSliders,cMaxFondSliders,0,aFondSliders), (cMinFondSliders,cMinFondSliders,0)), ("violet", "violette", (cMaxFondSliders,0,cMaxFondSliders,aFondSliders), (cMinFondSliders,0,cMinFondSliders)), ("orange", "orange", (cMaxFondSliders,(cMinFondSliders*0.7+0.3*cMaxFondSliders),0,aFondSliders), (cMinFondSliders,cMinFondSliders//2,0)), ("cyan", "cyan", (0,cMaxFondSliders,cMaxFondSliders,aFondSliders), (0,cMinFondSliders,cMinFondSliders))]
        longueurNomMaxPx = 1 * wTexteSliders#max(self.generateurTexte.creer_surface_texte(n, wTexteSliders, hTexteSliders, espacementTexteSliders).get_width() for n in lNomsConstantes)
        lCarSliders = [(nom, "cadre_barre_11.png", "carre_noir.png", f"carre_{couleur1}.png", f"forme_{couleur2}.png", rgbaFond, rgbTexte) for nom, (couleur1, couleur2, rgbaFond, rgbTexte) in zip(lNomsConstantes, lCouleursSliders)]
        yMinSliders = 0.1*self.jeu.hF#self.boutonPrediction.image.dimensions[1]*1.15
        hSlider = (self.jeu.hF - yMinSliders) / len(lNomsConstantes)
        assert len(lNomsConstantes) <= len(lCouleursSliders), "Plus de constantes que de couleurs disponibles"
        self.lSliders = []
        for iS, (nom,nomCadre,nomCarreNoir,nomCarreColore,nomForme,couleurFond,couleurTexte) in enumerate(lCarSliders):
            self.lSliders.append(Slider(self, self.police, self.dossier, self.dossierImagesBase, self.dossierImages, nom, longueurNomMaxPx, nomCadre, nomCarreNoir, nomCarreColore, nomForme, (0.03*self.jeu.wF, yMinSliders+iS*hSlider, 0.5*self.jeu.wF, 0.9*hSlider), (wTexteSliders, hTexteSliders, espacementTexteSliders), True, -1, 1, 13, None, couleurFond, couleurTexte, True))
        self.sliderProgressionEvaluation = Slider(self, self.police, self.dossier, self.dossierImagesBase, self.dossierImages, "Progression Evaluation", None, "cadre_barre_11.png", "carre_rouge.png", "carre_vert.png", "forme_jaune.png", (0.55*self.jeu.wF, 0.2*self.jeu.hF, 0.43*self.jeu.wF, 0.5*hSlider), (wTexteSliders, hTexteSliders, espacementTexteSliders), True, 0, 100, 20, 0, (cMaxFondSliders/2, cMaxFondSliders/2, cMaxFondSliders/2, aFondSliders), (cMinFondSliders/2, cMinFondSliders/2, cMinFondSliders/2), False)
        self.lSliders.append(self.sliderProgressionEvaluation)

        self.lNbNoeuds = [self.nbConstantes, 1]
        self.modele = self.jeu.algo.creer_reseau(self.lNbNoeuds)
        self.nbParties = nbParties

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

    def afficher(self):
        self.jeu.fenetre.fill((0,0,0))

        self.imFond.afficher(self.jeu.fenetre)
        self.texteApprentissage.afficher(self.jeu.fenetre)
        self.boutonHome.afficher(self.jeu.fenetre)
        self.boutonPrediction.afficher(self.jeu.fenetre)
        for slider in self.lSliders:
            slider.afficher(self.jeu.fenetre)
      
        pygame.display.flip()

    def evaluation(self):
        lValeurs = [slider.valeur for slider in self.lSliders[:self.nbConstantes]]
        dicoReseau = {'0.weight' : torch.tensor(lValeurs, dtype=torch.float32).unsqueeze(0), '0.bias' : torch.zeros(1, dtype=torch.float32)}
        self.modele.load_state_dict(dicoReseau)
        scoreMoyen, nbCoupsMoyen = self.jeu.algo.evaluation_algo(self.nbParties, self.modele, affichage=True, visuel=False, fonctionAvancement=self.lSliders[self.nbConstantes].changer_valeur)
        self.generateurNombre.afficher(self.jeu.fenetre, scoreMoyen, 0.55*self.jeu.wF, 0.3*self.jeu.hF, 0.05*self.jeu.wF, None)
        self.generateurNombre.afficher(self.jeu.fenetre, nbCoupsMoyen, 0.55*self.jeu.wF, 0.4*self.jeu.hF, 0.05*self.jeu.wF, None)

    def gerer_souris(self):
        if self.boutonHome.gerer_souris():
            self.actif = False
        if self.boutonPrediction.gerer_souris():
            self.evaluation()
        for slider in self.lSliders:
            slider.gerer_souris()

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
        alpha = pygame.surfarray.pixels_alpha(image2)
        rgb[:] = np.clip(rgb * facteur, 0, 255)
        return image2

    #def changer_couleur(self, dossier1, dossier2, dossier3, nom, lRGB, rgbM)




class Slider(object):
    def __init__(self, menu, police, dossier1, dossier2, dossier3, nom, wNomMax, nomCadre, nomCarreNoir, nomCarreColore, nomForme, rectangleFond, caracteristiquesTexte, enregistrement, valeurMin, valeurMax, nbValeurs, iValeur, couleurFond, couleurTexte, interactif):
        self.menu = menu
        self.interactif = interactif
        
        self.hover = False
        self.couleurFond = couleurFond
        self.xFond, self.yFond, self.wFond, self.hFond = rectangleFond
        self.fond = pygame.Surface((self.wFond, self.hFond), pygame.SRCALPHA)
        self.borderRadiusFond = round(min(self.fond.get_size())*0.3)
        
        wNomMax = police.render(nom, True, (0,0,0)).get_width() if wNomMax is None else wNomMax
        self.imCadre = Image(menu, dossier1, dossier2, dossier3, nomCadre, w=None, h=None, position=(0.15*self.wFond + caracteristiquesTexte[0]*self.wFond, 0.55*self.hFond), transparence=False, enregistrement=enregistrement)
        self.wCarres = 0.4*self.wFond / (nbValeurs-1+0.32)
        self.imCadre.dimensions = (0.4*self.wFond, 1.21*self.wCarres)
        self.imCadre.image = pygame.transform.smoothscale(self.imCadre.image, self.imCadre.dimensions)
        hCarres = 0.78*self.imCadre.dimensions[1]
        self.wCarres = hCarres*1.075
        self.imCarreNoir = Image(menu, dossier1, dossier2, dossier3, nomCarreNoir, None, hCarres, None, False, enregistrement)
        self.imCarreColore = Image(menu, dossier1, dossier2, dossier3, nomCarreColore, None, hCarres, None, False, enregistrement)
        hForme = 0.7*hCarres
        self.imForme = Image(menu, dossier1, dossier2, dossier3, nomForme, None, hForme, None, True, enregistrement)
        self.xDebutCarres = self.imCadre.position[0] + 0.24*hCarres
        self.yDebutCarres = self.imCadre.position[1] + 0.13*hCarres

        self.nbValeurs = nbValeurs
        self.iValeur = self.nbValeurs//2 if iValeur is None else iValeur
        self.valeurMin, self.valeurMax = valeurMin, valeurMax
        self.deltaValeur = (self.valeurMax - self.valeurMin) / (self.nbValeurs-1)
        self.lValeurs = [float(f"{self.valeurMin+i*self.deltaValeur:.2f}") for i in range(self.nbValeurs)]
        self.valeur = self.lValeurs[self.iValeur]
        self.lPositionsCarres = [(self.xDebutCarres+i*self.wCarres, self.yDebutCarres) for i in range(self.nbValeurs)]
        self.lPositionsForme = [(xC-self.imForme.dimensions[0]/2-(self.wCarres-self.imCarreNoir.dimensions[0])/2, yC+0.5*(hCarres-self.imForme.dimensions[1])) for i,(xC,yC) in enumerate(self.lPositionsCarres)]
        self.lPositionsCarres.pop()

        self.police = police
        self.couleurTexte = couleurTexte
        self.maj_valeur_min()
        self.maj_valeur_max()
        self.maj_valeur()
        self.maj_nom(nom, caracteristiquesTexte)

        self.bouge = False
        self.xSA, self.ySA = None,None

    def afficher(self, fenetre):
        self.fond.fill((0,0,0,0))
        couleurFond = tuple(map(lambda x : min(255, round(x*1.5)), (self.couleurFond))) if self.hover else self.couleurFond
        pygame.draw.rect(self.fond, couleurFond, self.fond.get_rect(), border_radius=self.borderRadiusFond)
        couleurBordFond = tuple(map(lambda x : min(255, round(x*0.5)), (couleurFond[:3]))) + (couleurFond[3],) if self.bouge else couleurFond
        pygame.draw.rect(self.fond, couleurBordFond, self.fond.get_rect(), border_radius=self.borderRadiusFond, width=round(self.hFond/15))
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
        #self.menu.generateurTexte.afficher(self.fond, str(self.valeur), *self.positionTexteV, 0.01*self.menu.jeu.wF, self.texteValeur.get_height(), 0.1, "centre")
        self.fond.blit(self.texteNom, self.positionTexteNom)
        #self.menu.generateurTexte.afficher(self.fond, "C tt bon bg", *self.positionTexteNom, 0.01*self.menu.jeu.wF, self.texteNom.get_height(), 0.1, "gauche")

        fenetre.blit(self.fond, (self.xFond, self.yFond))

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
        #self.texteValeur = self.police.render(str(self.valeur), True, self.couleurTexte)
        self.texteValeur = self.menu.generateurTexte.creer_surface_texte(str(self.valeur), 0.2*self.wFond, 0.3*self.hFond, 0.1)
        self.positionTexteV = (self.imCadre.position[0]+(self.imCadre.dimensions[0]-self.texteValeur.get_width())/2, self.imCadre.position[1]-self.texteValeur.get_height()-0.05*self.hFond)

    def maj_valeur_min(self):
        #self.texteValeurMin = self.police.render(str(self.valeurMin), True, self.couleurTexte)
        self.texteValeurMin = self.menu.generateurTexte.creer_surface_texte(str(self.valeurMin), 0.2*self.wFond, 0.3*self.hFond, 0.05)
        self.positionTexteVMin = (self.imCadre.position[0]-(self.texteValeurMin.get_width()+self.imCarreNoir.image.get_width()/2), self.imCadre.position[1]+(self.imCadre.dimensions[1]-self.texteValeurMin.get_height())/2)       

    def maj_valeur_max(self):
        #self.texteValeurMax = self.police.render(str(self.valeurMax), True, self.couleurTexte)
        self.texteValeurMax = self.menu.generateurTexte.creer_surface_texte(str(self.valeurMax), 0.2*self.wFond, 0.3*self.hFond, 0.05)
        self.positionTexteVMax = (self.imCadre.position[0]+self.imCadre.dimensions[0]+self.imCarreNoir.image.get_width()/2, self.imCadre.position[1]+(self.imCadre.dimensions[1]-self.texteValeurMax.get_height())/2)
    
    def maj_nom(self, nom, caracteristiquesTexte):
        #self.texteNom = self.police.render(nom, True, self.couleurTexte)
        wT, hT, eT = caracteristiquesTexte
        wTexte = wT*self.wFond
        hTexte = hT*self.hFond
        self.texteNom = self.menu.generateurTexte.creer_surface_texte(nom, wTexte, hTexte, eT)
        self.positionTexteNom = (0.03*self.wFond + (wTexte-self.texteNom.get_width())/2, self.imCadre.position[1])#(self.hFond-self.texteNom.get_height())/2)




class Generateur_Texte(object):
    def __init__(self, menu, dossier1, dossier2, dossier3, dicoNoms, transparence, enregistrement):
        self.menu = menu
        self.lImages = {nom : Image(menu, dossier1, dossier2, dossier3, nomFichier, None, None, None, transparence, enregistrement) for nom,nomFichier in dicoNoms.items()}
        self.dicoImagesVu = {}

    def recuperer_image(self, nom, w, h):
        cle = (nom, w, h)
        if cle in self.dicoImagesVu:
            return self.dicoImagesVu[cle]
        image, _ = self.menu.modifier_dimensions(self.lImages[nom].image, w, h)
        self.dicoImagesVu[cle] = image
        return image

    def creer_surface_texte(self, texte, wTotal, hTotal, espacement):
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
        surface = pygame.Surface((wTotal, hI), pygame.SRCALPHA)
        #surface.set_alpha(0) #transparent
        #surface.fill((0,0,0,100))
        x = 0
        for image in lImages:
            surface.blit(image, (x, 0))
            x += image.get_width() + wEspacement
        return surface      

class Bouton(object):
    def __init__(self, menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement):
        self.menu = menu
        self.image = Image(self.menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement)
        self.imageNormal = self.image.image.copy()
        self.imageHover = self.menu.changer_couleur(self.imageNormal, 1.3)
        self.imagePressed = self.menu.changer_couleur(self.imageNormal, 0.8)
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
    def __init__(self, menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement):
        self.menu = menu
        self.image, self.dimensions = self.menu.ouvrir_image(dossier1, dossier2, nom, dossier3, w, h, transparence, enregistrement)
        self.position = position
    def afficher(self, fenetre, position=None):
        self.position = self.position if position is None else position
        fenetre.blit(self.image, self.position)
    def tester_hover(self, xS=None, yS=None):
        if xS is None or yS is None:
            xS, yS = pygame.mouse.get_pos()
        return (self.position[0] <= xS <= self.position[0]+self.dimensions[0]) and (self.position[1] <= yS <= self.position[1]+self.dimensions[1])