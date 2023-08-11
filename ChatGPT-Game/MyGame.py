import pygame
import random

from pond import Pond
from plant import Algae

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 10
DAMPING = 0.98
RIPPLE_FPS = 20
FPS = 60
WHITE = (255, 255, 255)
backgroundColor = (90, 190, 255)

#Few values to add
num_algae = 10
rainfall = 2 #determines how many ripples are generated per loop
rainfall_strength = 5

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fish and Algae Simulation")

# Initialize the pond
pond = Pond(backgroundColor,SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, RIPPLE_FPS, DAMPING)

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
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #pond.simulate()
    pond.update(dt)
    
    for c in range(rainfall):
        pond.add_ripple(random.randint(0, SCREEN_WIDTH),random.randint(0, SCREEN_HEIGHT),rainfall_strength) # generate a random ripple
    pond.draw(screen)

    #clock.tick(FPS)

pygame.quit()