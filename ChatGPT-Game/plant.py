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
        self.weight = 0.002 # -> 20g


    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Algae(Plant):
    def __init__(self, x, y, environment):
        super().__init__(algae_image, x, y, environment)
        #variables defined by the parent class: 
        #image, rect, environment
        self.eatable = True
        self.lateral_speed = 50  # Adjust this value as needed

    def update(self, dt):
        # Calculate the algae's new position based on the heightmap and lateral speed (weight)
        if self.weight != 0:
            lateral_speed = 1/self.weight
        else: 
            lateral_speed = 0
        heightmap = self.environment.ripple_simulator        
        lateral_displacement_x = heightmap.get_height_at(self.rect.x + 5, self.rect.y) - heightmap.get_height_at(self.rect.x - 5, self.rect.y)
        lateral_displacement_y = heightmap.get_height_at(self.rect.x, self.rect.y + 5) - heightmap.get_height_at(self.rect.x, self.rect.y - 5)
        self.rect.x -= lateral_displacement_x * lateral_speed*dt
        self.rect.y -= lateral_displacement_y * lateral_speed*dt
        
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)