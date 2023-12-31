# pond.py

import pygame
import numpy as np
import random
from ripplesimulator import RippleSimulator
from flowfield import flowfield
from plant import Algae

# Pond class
class Pond:
    def __init__(self, background, width, height, cell_size, EffectFPS, damping, fluctuation_strength,num_algae):
        self.organisms = []
        self.waves = []
        self.background = background
        self.width = width
        self.height = height
        self.rainfall = 0
        self.rainfall_strength = 5
        self.cell_size = cell_size
        self.ripple_simulator = RippleSimulator(width, height, cell_size, 1/EffectFPS, damping, background)
        self.flow_field = self.flow_field = flowfield(self.width, self.height, cell_size, 1/EffectFPS, fluctuation_strength)
        self.time_passed = 0
        self.fov_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.num_algae = num_algae
        self.generation = 0

    def add_organism(self, organism):
        self.organisms.append(organism)
    
    def update(self, dt):
        self.time_passed += dt
        if self.time_passed > 0.1:
            self.spawn_food()
        if self.rainfall != 0:
            if self.time_passed >= 1/self.rainfall:
                self.time_passed -= 1/self.rainfall
                self.add_ripple(random.randint(0, self.width),random.randint(0, self.height),self.rainfall_strength) # generate a random ripple
        self.ripple_simulator.update(dt)
        self.flow_field.update(dt)
        for organism in self.organisms:
            organism.update(dt)
        
    def add_ripple(self, x, y, strength):
        self.ripple_simulator.add_ripple(x, y, strength)
    
    def rain(self, rainfall, rainfall_strength):
        self.rainfall = rainfall
        self.rainfall_strength = rainfall_strength
    
    def spawn_food(self):
        counter = 0
        for organism in self.organisms:
            if isinstance(organism, Algae):
                counter += 1
        if (counter != self.num_algae):
            for i in range(self.num_algae-counter):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                algae = Algae(x, y, self)
                self.add_organism(algae)
            
    
    def update_heightmap(self, damping):
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                neighbor_heights = [
                    self.heightmap[y + dy, x + dx]
                    for dy in range(-1, 2)
                    for dx in range(-1, 2)
                    if 0 <= y + dy < self.grid_height and 0 <= x + dx < self.grid_width
                ]
                new_height = np.mean(neighbor_heights) * damping
                self.heightmap[y, x] = new_height

    def draw(self, screen):        
        self.ripple_simulator.draw(screen)
        
        self.fov_surface.fill((0, 0, 0, 0))
        
        for organism in self.organisms:
            organism.draw(screen)
        
        screen.blit(self.fov_surface, (0,0))