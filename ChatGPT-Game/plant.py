# plant.py

import pygame

algae_image = pygame.image.load("Sprites/algae2.png")

class Plant(pygame.sprite.Sprite):
    def __init__(self, image, x, y, environment):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.environment = environment
        self.eatable = False
        self.weight = 0

    def update(self, dt):
        pass

    def affected_by_heightmap(self, dt):
        # Calculate the algae's new position based on the heightmap and lateral speed (weight)
        if self.weight != 0:
            speed = 1/self.weight
        else: 
            speed = 0
        heightmap = self.environment.ripple_simulator        
        lateral_displacement_x = heightmap.get_height_at(self.rect.x + 5, self.rect.y) - heightmap.get_height_at(self.rect.x - 5, self.rect.y)
        lateral_displacement_y = heightmap.get_height_at(self.rect.x, self.rect.y + 5) - heightmap.get_height_at(self.rect.x, self.rect.y - 5)
        self.rect.x -= lateral_displacement_x * speed*dt
        self.rect.y -= lateral_displacement_y * speed*dt
    
    def affected_by_flow(self, dt):
        if self.environment.flow_field:
            speed = 1/self.weight
            grid_x = int(self.rect.x // self.environment.flow_field.cell_size)
            grid_y = int(self.rect.y // self.environment.flow_field.cell_size)
            flow_vector = self.environment.flow_field.get_flow_at(grid_x, grid_y)

            self.rect.x += flow_vector[0] * dt * speed
            self.rect.y += flow_vector[1] * dt * speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Algae(Plant):
    def __init__(self, x, y, environment):
        super().__init__(algae_image, x, y, environment)
        #variables defined by the parent class: 
        #image, rect, environment
        self.eatable = True
        self.weight = 0.002 # -> 20g

    def update(self, dt):
        self.affected_by_heightmap(dt) #atm used for the rain
        self.affected_by_flow(dt)
            
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)