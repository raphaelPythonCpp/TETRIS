from TETRIS_jeu_v8_raphael import*
from math import floor


pygame.init()

wFenetre, hFenetre = 800, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v8 Raphaël")
nbColonnes, nbLignes = 7, 12
tailleCase = min(0.4*wFenetre / nbColonnes, 0.8*hFenetre / nbLignes)

temps = pygame.time.Clock()
police = pygame.font.SysFont("Arial", 15, bold=True, italic=False)

game_infini = True
env = Jeu(fenetre=fenetre, police=police, tailleCase=tailleCase, nbColonnes=nbColonnes, nbLignes=nbLignes, nbFramesAffichage=1, entrainementGreedy=False, entrainementGenetique=True)

#env.algo.lConstantes = [-0.04, 0.15, 0.81, 0.89, 0.36, -0.0]
env.changer_game_nb_coups_max(game_infini)
env.changer_somme_nb_blocs(False)
nbParties = 10
for partie in range(1,nbParties+1):
    env.jouer(modeAlgo=False)
    print(f"Partie {partie} : Score {env.score} || Nb Coups : {env.nbCoups}")
    if env.quitterProgramme :
        break
pygame.quit()

"""
+ faire un algo troll qui fait de la merde jusqu'à genre hMax = nbLignes-4, et après il lance un bon algo
avec ça on peut mettre des noms genre \"C'est luther qui joue\" (<=> random) puis \"C'est Raphaël qui joue\" (bot brillant)

"""