import pygame
import random
import numpy as np

from pond import Pond
from plant import Algae
from animal import Fish
from animal import GeneticAlgorithm
from sidepanel import SidePanel

# Initialize Pygame
pygame.init()

#---Screen and effects---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
CELL_SIZE = 12 #for effects like ripples and flows
DAMPING = 0.98
EFFECT_FPS = 15
FPS = 60

SIDEPANEL_WIDTH = 200

#---colors---
WHITE = (255, 255, 255)
backgroundColor = (90, 190, 255)

#---fonts---
fontFPS = pygame.font.Font(None, 36)  # You can adjust the font size as needed


#Few values to add
num_algae = 10
num_fish = 20
rainfall = 10 #droplets per time intervall
rainfall_strength = 3 #strength of dingle droplet
currentfluctuation_strength = 0.03

# Create the screen
screen = pygame.display.set_mode((SIDEPANEL_WIDTH + SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fish and Algae Simulation")

#Create the sidepanel
side_panel = SidePanel(SCREEN_WIDTH, SIDEPANEL_WIDTH, SCREEN_HEIGHT)

# Parameters for genetic algorithm
generations = 50
        

# Initialize the pond
pond = Pond(backgroundColor,SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, EFFECT_FPS, DAMPING, currentfluctuation_strength)
pond.rain(rainfall, rainfall_strength)
side_panel.add_environment(pond) #Link pond to the panel to interchange data

# Create an instance of Algae and add it to the pond
for i in range(num_algae):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    algae = Algae(x, y, pond)
    pond.add_organism(algae)

fish_population = []    
for i in range(num_fish):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    fish = Fish(np.random.uniform(0, 1), x, y, pond)
    pond.add_organism(fish)
    fish_population.append(fish)
   
# Initialize genetic algorithm
ga = GeneticAlgorithm(fish_population, generations, pond)

#pond.add_organism(Fish(None, random.randint(0, SCREEN_WIDTH),random.randint(0, SCREEN_HEIGHT), pond))  
#--------------------------
#--------Game loop---------
#--------------------------
simulation_frame = 0
genetic_update_interval = 60
clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(30) / 1000.0
        
    #clear the screen
    screen.fill(backgroundColor)
    side_panel.render(clock)
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        side_panel.handle_event(event) #Pass events to sidepanel if not treated yet
            
    pond.update(dt)
    pond.draw(screen)
    side_panel.draw(screen, SCREEN_WIDTH)

    # Render FPS text
    fps_text = fontFPS.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))  # Adjust the position as needed
    pygame.display.flip()

    simulation_frame += 1

    # Update genetic algorithm at specified intervals
    if simulation_frame % genetic_update_interval == 0:
        #for fish in ga.population:
        ga.evolve_population()  
        print(f"Genetic Algorithm Update: Generation {ga.generations_completed}")

pygame.quit()