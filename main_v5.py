from TETRIS_jeu_v11_raphael import*
from math import floor

pygame.init()

wFenetre, hFenetre = 800, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v8 Raphaël")
nbColonnes, nbLignes = 5, 10
tailleCase = min(0.4*wFenetre / nbColonnes, 0.8*hFenetre / nbLignes)

horloge = pygame.time.Clock()
police = pygame.font.SysFont("Arial", 15, bold=True, italic=False)

game_infini = False
evaluation = False
env = Jeu(fenetre=fenetre, police=police, horloge=horloge,
          tailleCase=tailleCase, nbColonnes=nbColonnes, nbLignes=nbLignes, 
          visuel=True, nbFramesAffichage=1, lNbNoeuds=list(map(int, input("lNbNoeuds (ex : '7 8 1') : ").split())),
          entrainementGreedy=False, entrainementGenetique=False, entrainementNES=False, entrainementDRL=False)

env.changer_game_nb_coups_max(game_infini)
env.changer_somme_nb_blocs(False)
if not env.entrainementGenetique:
    with open("lDicoReseau_GA_NN.txt") as fichier:
        lDicoReseau = eval(fichier.read())
    iMax = max(i if dicoReseau is not None else -1 for i, dicoReseau in enumerate(lDicoReseau))
    if iMax > -1 :
        env.algo.charger_dico_reseau_sans_tensor(lDicoReseau[iMax])
    #env.algo.modele = Faux !
                          #[-0.33, -0.07, -0.66, -0.94, -0.42, 0.19, 0]
                          #[0.58, 0.02, 0.83, 0.27, 0.34, 0.69, 0]
                          #[0.98, 0.24, 0.35, 0.79, 0.05, 1, 0]
                          #[0.24, 0.65, 0.26, 0.77, 0.28, 1, 0]
                          #[0.51, 0.57, 0.89, -0.04, 0.19, 0.66, 0] => 516.7
                          #[0.27, 0.47, 0.22, 0.04, 0.06, 0.55, 0] => 525.5 (5x12)
                          #[0.33, 0.07, 0.66, 0.94, 0.42, 0.19, 0] => 
if evaluation and not env.quitterProgramme:
    env.algo.evaluation_algo(nbParties=200, modele=env.algo.modele, affichage=True, visuel=False)

if not env.quitterProgramme:
    env.tester_jeu(nbParties=10)

pygame.quit()

"""
+ faire un algo troll qui fait de la merde jusqu'à genre hMax = nbLignes-4, et après il lance un bon algo
avec ça on peut mettre des noms genre \"C'est luther qui joue\" (<=> random) puis \"C'est Raphaël qui joue\" (bot brillant)

"""