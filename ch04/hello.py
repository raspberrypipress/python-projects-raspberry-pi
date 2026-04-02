# Example file showing a circle moving on screen
import pygame
import pygame.freetype

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
running = True
dt = 0
font = pygame.freetype.Font("/home/ben/pybook/ch4-pygame/OpenSans-Regular.ttf", 24)

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #RENDER
    screen.fill("purple")
    
    text_surface, rect = font.render("Hello World!", (0, 0, 0))
    screen.blit(text_surface, (40, 250))

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
