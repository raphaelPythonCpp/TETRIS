from TETRIS_jeu_v9_raphael import*
from datetime import datetime
from math import floor

pygame.init()

wFenetre, hFenetre = 800, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v8 Raphaël")
nbColonnes, nbLignes = 5, 12
tailleCase = min(0.4*wFenetre / nbColonnes, 0.8*hFenetre / nbLignes)

temps = pygame.time.Clock()
police = pygame.font.SysFont("Arial", 15, bold=True, italic=False)

game_infini = True
env = Jeu(fenetre=fenetre, police=police, 
          tailleCase=tailleCase, nbColonnes=nbColonnes, nbLignes=nbLignes, 
          visuel=True, nbFramesAffichage=1, 
          entrainementGreedy=False, entrainementGenetique=False)

env.changer_game_nb_coups_max(game_infini)
env.changer_somme_nb_blocs(False)
if not env.entrainementGenetique:
    env.algo.lConstantes = [0.27, 0.47, 0.22, 0.04, 0.06, 0.55]
                          #[0.58, 0.02, 0.83, 0.27, 0.34, 0.69]
                          #[0.98, 0.24, 0.35, 0.79, 0.05, 1]
                          #[0.24, 0.65, 0.26, 0.77, 0.28, 1]
                          #[0.51, 0.57, 0.89, -0.04, 0.19, 0.66] => 516.7
                          #[0.27, 0.47, 0.22, 0.04, 0.06, 0.55] => 525.5
else :
    env.evaluation_algo(nbParties=1000)

env.tester_jeu(nbParties=10)

pygame.quit()

"""
+ faire un algo troll qui fait de la merde jusqu'à genre hMax = nbLignes-4, et après il lance un bon algo
avec ça on peut mettre des noms genre \"C'est luther qui joue\" (<=> random) puis \"C'est Raphaël qui joue\" (bot brillant)

"""