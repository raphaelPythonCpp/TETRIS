from collections import deque
import pygame

def modifier_dimensions(image, w=None, h=None):
    if w is not None:
        wI, hI = image.get_size()
        facteur = w / wI
        dimensions2 = (int(wI * facteur), int(hI * facteur))
        image2 = pygame.transform.smoothscale(image, dimensions2)
    elif h is not None:
        wI, hI = image.get_size()
        facteur = h / hI
        dimensions2 = (int(wI * facteur), int(hI * facteur))
        image2 = pygame.transform.smoothscale(image, dimensions2)
    else :
        image2 = image.copy()
        dimensions2 = image.get_size()
    return image2, dimensions2

def ouvrir_image(dossier1, dossier2, nom, dossier3=None, w=None, h=None, transparence=False, enregistrement=False):
    chemin = f"{dossier1}\\{dossier2}\\{nom}"
    image = pygame.image.load(chemin).convert_alpha() if transparence else pygame.image.load(chemin).convert()
    image, dimensions = modifier_dimensions(image, w, h)
    if enregistrement:
        pygame.image.save(image, f"{dossier1}\\{dossier3}\\{nom}")
    return image, dimensions

def extraire_tous_images(dossier1, dossier2, dossier3, nom, lNomsBoutons):
    imageAsset, (wA, hA) = ouvrir_image(dossier1, dossier2, nom, dossier3=None, w=None, h=None, transparence=True, enregistrement=False)
    vu = [[imageAsset.get_at((x,y))[3] < 30 for x in range(wA)] for y in range(hA)]
    lDXY = lDXY = [(1,0), (-1,0), (0,1), (0,-1)] # [(x,y) for x in range(-1,2) for y in range(-1,2) if x != 0 or y != 0]
    lImages = []
    for Y in range(hA):
        for X in range(wA):
            if vu[Y][X]: 
                continue
            vu[Y][X] = True
            file = deque([(X,Y)])
            sPixels = set()
            xMin,xMax,yMin,yMax = X,X,Y,Y
            while file:
                x,y = file.popleft()
                sPixels.add((x,y))
                for dx,dy in lDXY:
                    x2, y2 = x+dx, y+dy
                    if (0 <= x2 < wA) and (0 <= y2 < hA) and not vu[y2][x2]:
                        vu[y2][x2] = True
                        file.append((x2,y2))
                        xMin = min(xMin, x2)
                        xMax = max(xMax, x2)
                        yMin = min(yMin, y2)
                        yMax = max(yMax, y2)

            image2 = imageAsset.subsurface((xMin, yMin, xMax-xMin+1, yMax-yMin+1)).copy()
            nbPixelsVide = 0
            sommeTransparence = 0
            for x in range(xMin, xMax+1):
                for y in range(yMin, yMax+1):
                    if (x,y) not in sPixels:
                        image2.set_at((x-xMin,y-yMin), (0,0,0,0))
                        nbPixelsVide += 1
                    elif x > xMin+5 and y > yMin+5 :
                        sommeTransparence += image2.get_at((x-xMin,y-yMin))[3]
            nbPixels = ((xMax-xMin+1)*(yMax-yMin+1))
            #print(len(lImages), nbPixelsVide/nbPixels)
            if nbPixelsVide/nbPixels <= 0.45 and sommeTransparence/(nbPixels-nbPixelsVide) >= 150:
                lImages.append(image2)
    lNomsBoutons = lNomsBoutons+[i for i in range(len(lImages)-len(lNomsBoutons))] if lNomsBoutons is not None else [i for i in range(len(lImages))]
    for image, nomBouton in zip(lImages, lNomsBoutons):
        pygame.image.save(image, f"{dossier1}\\{dossier3}\\{nomBouton}.png")
    pygame.image.save(imageAsset, f"{dossier1}\\{dossier3}\\asset.png")

class Generateur_Nombre(object):
    def __init__(self, menu, dossier1, dossier2, dossier3, lNoms, transparence, enregistrement):
        self.menu = menu
        self.lImages = {nom : Image(menu, dossier1, dossier2, dossier3, nomFichier, None, None, None, transparence, enregistrement) for nom,nomFichier in lNoms}
    
    def afficher(self, fenetre, nombre, x, y, w, h):
        for i,car in enumerate(str(nombre)):
            car = int(car)
            assert 0 <= car <= 9, "Caractère faux dans nombre"
            image2, dim2 = self.menu.modifier_dimensions(self.lImages[car].image, w, h)
            fenetre.blit(image2, (x+i*dim2[0], y))

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

pygame.init()

wFenetre, hFenetre = 800, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v8 Raphaël")
nbColonnes, nbLignes = 5, 10
tailleCase = min(0.4*wFenetre / nbColonnes, 0.8*hFenetre / nbLignes)

horloge = pygame.time.Clock()
police = pygame.font.SysFont("Arial", 15, bold=True, italic=False)

lNoms = "gauche droite changer changer2 autre aide info vide confirmer annuler accueil options succes collections calendrier boutique cadeau coffre mail calendrier none profile amis messages clan cible sauvegarder telecharger partager video photo none glace vide attaque bouclier cible ennemie danger bombe electricite feu jouer pause stop avancer reculer monnaie gamme cle carte inventaire journal son silencieux musique manette plein ecran deconnexion verrouiller deverouiller poubelle modifier reinitialiser".split()
extraire_tous_images("MENU_DIDACTIQUE", "IMAGES_BASE", "IMAGES_UTILES", "asset_icons.png", lNoms)

pygame.quit()