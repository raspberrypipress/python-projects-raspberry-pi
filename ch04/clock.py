import pygame
import pygame.freetype
import datetime
import textwrap

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
running = True
dt = 0
font = pygame.freetype.Font("/path/to/OpenSans-Regular.ttf", 250)

words = [
    "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "eleven", "twelve", "thirteen",
    "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
    "nineteen", "twenty", "twenty one", "twenty two",
    "twenty three", "twenty four", "twenty five", "twenty six",
    "twenty seven", "twenty eight", "twenty nine", "thirty"]

display_width_chars = 15
line_height = 210

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    current_time = datetime.datetime.now()
    hours = current_time.hour
    mins = current_time.minute
    
    text = "It is now "
    half = " in the morning"
    if hours > 12:
         hours -= 12
         half = " in the afternoon"
    if (mins == 0):
        text += words[hours - 1] + " o'clock" 
    elif (mins < 31):      
        text += words[mins - 1] + " minutes past " 
        text += words[hours - 1]
    else:
        text += words[(60 - mins - 1)] + " minutes to "
        text += words[hours]
        
    text += half

    lines = textwrap.wrap(text, display_width_chars)

    # RENDER
    screen.fill("aquamarine")
    y = 20
    for line in lines:
        text_surface, rect = font.render(line, (0, 0, 0))
        screen.blit(text_surface, (40, y))
        y = y+line_height
    pygame.display.flip()
    dt = clock.tick(60) / 1000
pygame.quit()
