from TETRIS_jeu_v4_raphael import*


pygame.init()

wFenetre, hFenetre = 600, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v4 Raphaël")

temps = pygame.time.Clock()
police = pygame.font.SysFont("Arial", 20, bold=False, italic=False)

"""+faire font pour afficher le score"""

env = Jeu(fenetre=fenetre, police=police, tailleCase=30, nbColonnes=10, nbLignes=16, visuel=False)

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

with open("dico_comparatif_lConstantes.txt", "w") as fichier:
    fichier.write(str(dicoRes))
pygame.time.delay(5000)
pygame.quit()