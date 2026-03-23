from TETRIS_jeu_v7_raphael import*
from math import floor


pygame.init()

wFenetre, hFenetre = 600, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v6 Raphaël")

temps = pygame.time.Clock()
police = pygame.font.SysFont("Arial", 15, bold=True, italic=False)

game_infini = True
env = Jeu(fenetre=fenetre, police=police, tailleCase=30, nbColonnes=9, nbLignes=18, visuel=True)

trouver_meilleurs_constantes = False
if trouver_meilleurs_constantes:
    env.visuel = False
    env.changer_game_nb_coups_max(False)
    env.changer_somme_nb_blocs(True)
    nbParties = 10
    lConstantes = [0] * env.algo.nbConstantes
    #lConstantes = [0, 0, 0, 0.5, 0.5, 0.5]
    pasConstantes = 0.5
    nbCombinaisons = floor(1/pasConstantes + 1)**len(lConstantes)
    iCombinaison = 0
    dicoRes = {}
    while lConstantes[0] <= 1 and not env.quitterProgramme:
        iCombinaison += 1
        print(f"lConstantes = {lConstantes} || {iCombinaison} / {nbCombinaisons} ({round(iCombinaison/nbCombinaisons, 2) * 100}%)")
        env.algo.lConstantes = lConstantes
        sommeScores = 0
        sommeNbCoups = 0
        sommeSommeSommeNbBlocs = 0
        for i in range(nbParties):
            env.jouer(modeAlgo=True)
            #print(f"Partie {i+1} : Score {env.score}")
            sommeScores += env.score
            sommeNbCoups += env.nbCoups
            sommeSommeSommeNbBlocs += env.sommeNbBlocs
            if env.quitterProgramme :
                break
        moyenneScores = sommeScores / nbParties
        moyenneNbCoups = sommeNbCoups / nbParties
        moyenneSommeSommeNbBlocs = sommeSommeSommeNbBlocs / nbParties
        print(f"==> scoreMoyen = {moyenneScores}")
        print(f"==> nbCoupsMoyen = {moyenneNbCoups}")
        print(f"==> moyenneSommeSommeNbBlocs = {moyenneSommeSommeNbBlocs}")
        dicoRes[tuple(lConstantes)] = moyenneScores
        #Changement lConstantes
        iC = len(lConstantes)-1
        lConstantes[iC] += pasConstantes
        while iC > 0 and lConstantes[iC] > 1:
            lConstantes[iC] = 0
            iC -= 1
            lConstantes[iC] += pasConstantes
        if env.quitterProgramme :
            break
    with open("dico_comparatif_lConstantes.txt", "w") as fichier:
        fichier.write(str(dicoRes))

else :
    env.changer_game_nb_coups_max(game_infini)
    env.changer_somme_nb_blocs(False)
    nbParties = 10
    for partie in range(1,nbParties+1):
        env.jouer()
        print(f"Partie {partie} : Score {env.score} || Nb Coups : {env.nbCoups}")
        if env.quitterProgramme :
            break
pygame.quit()

"""
+ faire un algo troll qui fait de la merde jusqu'à genre hMax = nbLignes-4, et après il lance un bon algo
avec ça on peut mettre des noms genre \"C'est luther qui joue\" (<=> random) puis \"C'est Raphaël qui joue\" (bot brillant)

"""