import pygame
import random

from pond import Pond
from plant import Algae

# Initialize Pygame
pygame.init()

#---Screen and effects---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 12 #for effects like ripples and flows
DAMPING = 0.98
EFFECT_FPS = 15
FPS = 60

#---colors---
WHITE = (255, 255, 255)
backgroundColor = (90, 190, 255)

#---fonts---
fontFPS = pygame.font.Font(None, 36)  # You can adjust the font size as needed


#Few values to add
num_algae = 10
rainfall = 0 #droplets per time intervall
rainfall_strength = 3 #strength of dingle droplet
currentfluctuation_strength = 0.01

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fish and Algae Simulation")

# Initialize the pond
pond = Pond(backgroundColor,SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, EFFECT_FPS, DAMPING, currentfluctuation_strength)
pond.rain(rainfall, rainfall_strength)

# Create an instance of Algae and add it to the pond
for c in range(num_algae):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    algae = Algae(x, y, pond)
    pond.add_organism(algae)
    
#--------------------------
#--------Game loop---------
#--------------------------
clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(60) / 1000.0
    
    #clear the screen
    screen.fill(backgroundColor)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    pond.update(dt)
    pond.draw(screen)

    # Render FPS text
    fps_text = fontFPS.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))  # Adjust the position as needed
    pygame.display.flip()

pygame.quit()