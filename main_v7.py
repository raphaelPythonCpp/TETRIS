from TETRIS_jeu_v12_raphael import*
from math import floor

pygame.init()

wFenetre, hFenetre = 800, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v12 Raphaël")
nbColonnes, nbLignes = 10, 22
tailleCase = min(0.4*wFenetre / nbColonnes, 0.8*hFenetre / nbLignes)

horloge = pygame.time.Clock()
nomPolice, taillePolice, grasPolice, italiquePolice = "Arial", 20, True, False
lAttributsPolice = (nomPolice, taillePolice, grasPolice, italiquePolice)
police = pygame.font.SysFont(nomPolice, taillePolice, bold=grasPolice, italic=italiquePolice)

game_infini = False
charger_reseau = False
evaluation = False
env = Jeu(fenetre=fenetre, lAttributsPolice=lAttributsPolice, horloge=horloge,
          tailleCase=tailleCase, nbColonnes=nbColonnes, nbLignes=nbLignes,
          visuel=True, menus=True, nbFramesAffichage=1, lNbNoeuds=None,
          algorithme=False, entrainementGreedy=False, entrainementGenetique=False, entrainementNES=False, entrainementDRL=False,
          gameInfini=game_infini)

env.changer_game_nb_coups_max(game_infini)
env.changer_somme_nb_blocs(False)
if not env.entrainementGenetique and charger_reseau:
    with open("lDicoReseau_GA_NN.txt") as fichier:
        lDicoReseau = eval(fichier.read())
    iMax = max(i if dicoReseau is not None else -1 for i, dicoReseau in enumerate(lDicoReseau))
    if iMax > -1 :
        env.algo.charger_dico_reseau_sans_tensor(lDicoReseau[iMax])
    else :
        print("Pas de Dico Reseau disponible !")

if evaluation and not env.quitterProgramme and env.algorithme:
    env.algo.evaluation_algo(nbParties=int(input("nbParties Evaluation : ")), modele=env.algo.modele, affichage=True, visuel=False)

if not env.quitterProgramme:
    env.tester_jeu(nbParties=10)

pygame.quit()

"""
+ faire un algo troll qui fait de la merde jusqu'à genre hMax = nbLignes-4, et après il lance un bon algo
avec ça on peut mettre des noms genre \"C'est luther qui joue\" (<=> random) puis \"C'est Raphaël qui joue\" (bot brillant)

"""