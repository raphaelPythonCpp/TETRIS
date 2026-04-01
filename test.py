from time import sleep

nbG = 10
nbP = 3
print('\n\n')
for iG in range(nbG):
    for iP in range(nbP):
        print("\033[F\033[F", end="")
        print("Coucou !")
        print(f"Génération {iG} Partie {iP}")
        sleep(0.2)