import pygame

pygame.init()
fenetre = pygame.display.set_mode((200,200))
xC, yC, wC, hC = (90,90,20,20)
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            xS, yS = pygame.mouse.get_pos()
            if (xC <= xS <= xC+wC) and (yC <= yS <= yC+hC):
                run = False
    fenetre.fill((0,0,0))
    pygame.draw.rect(fenetre, (0,0,255), (xC, yC, wC, hC))
    pygame.display.flip()
    for i in range(10000):
        print('\r',i, end='', flush=True)
    print()

pygame.quit()