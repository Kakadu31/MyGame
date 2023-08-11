# pond.py

import pygame
import numpy as np
from ripplesimulator import RippleSimulator

# Pond class
class Pond:
    def __init__(self, background, width, height, cell_size, rippleFPS, damping):
        self.organisms = []
        self.waves = []
        self.background = background
        self.width = width
        self.height = height
        self.ripple_simulator = RippleSimulator(width, height, cell_size, 1/rippleFPS, damping, background)

    def add_organism(self, organism):
        self.organisms.append(organism)

    def update(self, dt):
        self.ripple_simulator.update(dt)
        for organism in self.organisms:
            organism.update(dt)
        
    def add_ripple(self, x, y, strength):
        self.ripple_simulator.add_ripple(x, y, strength)

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
        screen.fill(self.background)
        
        self.ripple_simulator.draw(screen)
        
        for organism in self.organisms:
            organism.draw(screen)
        
        pygame.display.flip()