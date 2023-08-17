import pygame
import numpy as np
import random

fish_image = pygame.image.load("Sprites/fish2.png")

# Define the Fish class
class Animal(pygame.sprite.Sprite):
    def __init__(self, hunting_behaviour, image, x, y, environment):
        super().__init__()
        self.fitness = 0
        self.hunting_behaviour = hunting_behaviour
        
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
            speed = 10/self.weight
        else: 
            speed = 0
        heightmap = self.environment.ripple_simulator        
        lateral_displacement_x = heightmap.get_height_at(self.rect.x + 10, self.rect.y) - heightmap.get_height_at(self.rect.x - 10, self.rect.y)
        lateral_displacement_y = heightmap.get_height_at(self.rect.x, self.rect.y + 10) - heightmap.get_height_at(self.rect.x, self.rect.y - 10)
        
        self.rect.x -= lateral_displacement_x * speed*dt
        self.rect.y -= lateral_displacement_y * speed*dt
        self.check_boundaries()

    
    def affected_by_flow(self, dt):
        if self.environment.flow_field:
            speed = 1/self.weight
            grid_x = int(self.rect.x // self.environment.flow_field.cell_size)
            grid_y = int(self.rect.y // self.environment.flow_field.cell_size)
            flow_vector = self.environment.flow_field.get_flow_at(grid_x, grid_y)

            self.rect.x += flow_vector[0] * dt * speed
            self.rect.y += flow_vector[1] * dt * speed
            self.check_boundaries()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def check_boundaries(self):
        self.rect.x = np.clip(self.rect.x, 10, self.environment.width - 11)
        self.rect.y = np.clip(self.rect.y, 10, self.environment.height - 11)


class Fish(Animal):
    def __init__(self, hunting_behaviour, x, y, environment):
        super().__init__(hunting_behaviour, fish_image, x, y, environment)
        self.weight = 0.05
    
    def update(self, dt):
        self.affected_by_heightmap(dt) #atm used for the rain
        self.affected_by_flow(dt)
            
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)


# Genetic Algorithm Setup
class GeneticAlgorithm:
    def __init__(self, population, generations):
        self.population = population
        self.generations = generations
        self.generations_completed = 0
    
    def select_parents(self):
        parents = np.random.choice(self.population, size=2, replace=False)
        return parents[0], parents[1]
    
    def crossover(self, parent1, parent2):
        offspring_behaviour = (parent1.hunting_behaviour + parent2.hunting_behaviour) / 2
        return Fish(offspring_behaviour, parent1.rect.x, parent2.rect.y, parent1.environment)
    
    def mutate(self, fish):
        mutation_rate = 0.1
        fish.hunting_behaviour += np.random.uniform(-mutation_rate, mutation_rate)
        fish.hunting_behaviour = np.clip(fish.hunting_behaviour, 0, 1)
    
    def evolve_population(self):
        new_population = []
        for _ in range(len(self.population)):
            parent1, parent2 = self.select_parents()
            offspring = self.crossover(parent1, parent2)
            if np.random.rand() < 0.1:  # 10% chance of mutation
                self.mutate(offspring)
            new_population.append(offspring) #Add the offsping to the genetic algorithms population
            offspring.environment.add_organism(offspring) #Add the offsping to the environments population
        self.population = new_population
        self.generations_completed += 1 