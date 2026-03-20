from TETRIS_jeu_v5_raphael import*


pygame.init()

wFenetre, hFenetre = 600, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v5 Raphaël")

temps = pygame.time.Clock()
police = pygame.font.SysFont("Arial", 20, bold=False, italic=False)

"""+faire font pour afficher le score"""

env = Jeu(fenetre=fenetre, police=police, tailleCase=30, nbColonnes=9, nbLignes=18, visuel=True)

trouver_meilleurs_constantes = False
if trouver_meilleurs_constantes:
    env.visuel = False
    nbParties = 50
    lConstantes = [0, 0, 0, 0]
    pasConstantes = 0.2
    dicoRes = {}
    while lConstantes[0] <= 1:
        print(f"lConstantes = {lConstantes}")
        env.algo.lConstantes = lConstantes
        sommeScores = 0
        for i in range(nbParties):
            env.reset()
            env.changer_mode_algo()
            env.jouer()
            #print(f"Partie {i+1} : Score {env.score}")
            sommeScores += env.score
        moyenneScores = sommeScores / nbParties
        print(f"==> scoreMoyen = {moyenneScores}")
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
    nbParties = 10
    for partie in range(1,nbParties+1):
        env.reset()
        env.jouer()
        print(f"Partie {partie} : Score {env.score} || Nb Coups : {env.nbCoups}")
        if env.quitterProgramme :
            break
pygame.quit()