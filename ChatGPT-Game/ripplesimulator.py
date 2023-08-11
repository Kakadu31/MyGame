# ripplesimulator.py

import pygame
import numpy as np
import colorsys

class RippleSimulator:
    def __init__(self, width, height, cell_size, time_interval, damping, background):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.time_interval = time_interval
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size
        self.damping = damping
        self.heightmap = np.zeros((self.grid_height, self.grid_width))
        self.background = background
        self.time_passed = 0

    def add_ripple(self, x, y, strength):
        grid_x = x // self.cell_size
        grid_y = y // self.cell_size
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self.heightmap[grid_y, grid_x] = strength
    
    def update(self, dt):
        self.time_passed += dt
        if self.time_passed >= self.time_interval:
            self.time_passed -= self.time_interval
            self.update_heightmap()
        
    def update_heightmap(self):
        new_heightmap = np.zeros_like(self.heightmap)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                neighbor_heights = [
                    self.heightmap[y + dy, x + dx]
                    for dy in range(-1, 2)
                    for dx in range(-1, 2)
                    if 0 <= y + dy < self.grid_height and 0 <= x + dx < self.grid_width
                ]
                new_height = np.mean(neighbor_heights) * self.damping
                new_heightmap[y, x] = new_height
        self.heightmap = new_heightmap
    
    def get_height_at(self, x, y):
        grid_x = int(x // self.cell_size)
        grid_y = int(y // self.cell_size)
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return self.heightmap[grid_y, grid_x]
        return 0  # Default height when outside the grid
    
    def draw(self, screen):
        r, g, b = self.background[0], self.background[1], self.background[2]
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                heightmap_value = np.clip(self.heightmap[y,x], -1, 1)
                new_l = (l+l*heightmap_value)/2
                new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_l, s)
                new_r, new_g, new_b = int(new_r*255), int(new_g*255), int(new_b*255)
                color = (new_r, new_g, new_b)
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, color, rect)
                