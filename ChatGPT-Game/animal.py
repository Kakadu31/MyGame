import pygame
import numpy as np
import random, math
from neuralnetwork import NeuralNetwork
from plant import Algae
from cmath import pi

sexes = ["male", "female"]
fish_image_male = pygame.image.load("Sprites/fish3_male.png")
fish_image_female = pygame.image.load("Sprites/fish3_female.png")

# Define the Fish class
class Animal(pygame.sprite.Sprite):
    def __init__(self, hunting_behaviour, image, x, y, environment):
        super().__init__()
        self.fitness = 0
        self.hunting_behaviour = hunting_behaviour
                   
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity = (0,0)
        self.angle = 0 #math.pi
        self.environment = environment
        
        self.field_of_view_radius = 150
        self.field_of_view_angle = math.radians(90)
        self.fov_vertices = [self.rect.center,self.rect.center,self.rect.center]
        self.show_fov = True
        
        self.nn_input_size = 8
        self.nn_hidden_size = 8
        self.nn_output_size = 2
        self.neural_network = NeuralNetwork(self.nn_input_size, self.nn_hidden_size, self.nn_output_size)
        
        self.eatable = False
        self.sex = random.choice(sexes)
        self.age = 0
        self.weight = 0
        self.speed = 0
        self.encountered_animals = []
        
        self.encounter_distance_threshold = 2*environment.cell_size
        self.procreation_age = 0
        self.pregnancy_term = 120
        self.pregnancy_time = 0
        self.offspring = None
        
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

    def encounter(self, other_animal_population):
        # Iterate through other fish and check distances
        self.encountered_animals = []  # Clear the list of encountered fish
        for other_animal in other_animal_population:
            if self != other_animal:  # Exclude self
                distance = np.linalg.norm(np.array([self.rect.x, self.rect.y]) - np.array([other_animal.rect.x, other_animal.rect.y]))
                if distance < self.encounter_distance_threshold:
                    self.encountered_animals.append(other_animal)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def update_fov_surface(self):
        # Calculate the field of view vertices and draw the shape
        self.fov_vertices = self.calculate_fov_vertices()
        pygame.draw.polygon(self.environment.fov_surface, (255, 0, 0, 50), self.fov_vertices)

    def calculate_fov_vertices(self):
        # Calculate the vertices of the field of view triangle
        num_vertexes = 9
        vertexes = []
        offset = (self.rect.width // 2, self.rect.height //2)
        vertexes.append((self.rect.x + offset[0], self.rect.y+ offset[1]))
        
        c = -(num_vertexes-1)/2 
        for i in range(num_vertexes):            
            vertex = (
                int(self.rect.x + offset[0] + self.field_of_view_radius * math.cos(self.angle + c*self.field_of_view_angle / (num_vertexes-1))),
                int(self.rect.y + offset[1] + self.field_of_view_radius * math.sin(self.angle + c*self.field_of_view_angle / (num_vertexes-1))),
            )
            vertexes.append(vertex)
            c += 1
            i=i
        return vertexes
    
    def check_boundaries(self):
        self.rect.x = np.clip(self.rect.x, 10, self.environment.width - 11)
        self.rect.y = np.clip(self.rect.y, 10, self.environment.height - 11)
    
    def is_ready_to_mate(self):
        if (self.age >= self.procreation_age)&(self.pregnancy_time == 0):
            return True
        else:            return False
    
    def detect_algae(self):
        detected_algae = []
        for organism in self.environment.organisms:
            if (isinstance(organism, Algae)):
                if self.point_in_polygon(organism.rect.center, self.fov_vertices):
                    detected_algae.append((organism.rect.x, organism.rect.y))
        return detected_algae
        
    
    def point_in_polygon(self, point, polygon):
        x, y = point
        odd_nodes = False
        j = len(polygon) - 1
    
        for i in range(len(polygon)):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if yi < y and yj >= y or yj < y and yi >= y:
                if xi + (y - yi) / (yj - yi) * (xj - xi) < x:
                    odd_nodes = not odd_nodes
            j = i
        return odd_nodes

    def move(self, dt):
        detected_algae = self.detect_algae()
        # Construct inputs for the neural network with detected algae positions
        inputs = [self.rect.x, self.rect.y]
        for i in range(int((self.nn_input_size-2)/2)):
            if i < len(detected_algae):
                inputs += detected_algae[i]
            else:
                inputs += [0, 0]  # Placeholder for missing algae
        self.velocity = self.neural_network.feedforward(np.array(inputs))
        
        # Update fish position based on the velocity vector
        self.rect.x += self.velocity[0]*dt*self.speed
        self.rect.y += self.velocity[1]*dt*self.speed
        
        # Calculate the angle of the velocity vector and update the fish if necessary
        velocity_angle = math.atan2(self.velocity[1], self.velocity[0])
        if int(self.angle) != int(velocity_angle):
            self.image = pygame.transform.rotate(self.image, -int(math.degrees(velocity_angle)))
            self.angle = velocity_angle
                  
    def get_mating_partner(self):
        possible_partners = []
        #check for the other animals sex
        for other_animal in self.encountered_animals:
            if (other_animal.sex != self.sex)&(other_animal.is_ready_to_mate()):
                possible_partners.append(other_animal)
        #if there is a suitable partner, return it, else return none.
        if len(possible_partners) > 0:
            return np.random.choice(possible_partners, size=1, replace=False)[0]
        else: 
            return None

    def mate(self, partner, genetic_algorithm):
        #create an offspring from both partners
        self.offspring = genetic_algorithm.crossover(self, partner)
        if np.random.rand() < 0.1:  # 10% chance of mutation
            genetic_algorithm.mutate(self.offspring)
        self.pregnancy_time = 1
    
    def update_pregnancy_status(self, dt):
        if self.pregnancy_time:
            self.pregnancy_time += dt
            if self.pregnancy_time >= self.pregnancy_term:
                self.give_birth()
        
    def give_birth(self):
        #Add the offspring to the population, reset the pregnancy status
        self.offspring.age = 0
        self.environment.add_organism(self.offspring) #Add the offsping to the environments population
        self.pregnancy_time = 0
        self.offspring = None

class Fish(Animal):
    def __init__(self, hunting_behaviour, x, y, environment):
        super().__init__(hunting_behaviour, fish_image_male, x, y, environment)
        if (self.sex == "male"):
            self.image = fish_image_male
        else:
            self.image = fish_image_female
        self.weight = 0.05
        self.speed = 15
    
    def update(self, dt):
        self.move(dt)
        self.affected_by_heightmap(dt) #atm used for the rain
        self.affected_by_flow(dt)
        self.age += dt
        self.update_pregnancy_status(dt)

            
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        
        if self.show_fov:
            self.update_fov_surface()
    

# Genetic Algorithm Setup
class GeneticAlgorithm:
    def __init__(self, population, generations, environment):
        self.population = population
        self.generations = generations
        self.environment = environment
        self.generations_completed = 0
    
    def crossover(self, parent1, parent2):
        offspring_behaviour = (parent1.hunting_behaviour + parent2.hunting_behaviour) / 2
        return Fish(offspring_behaviour, parent1.rect.x, parent2.rect.y, parent1.environment)
    
    def mutate(self, animal):
        mutation_rate = 0.1
        animal.hunting_behaviour += np.random.uniform(-mutation_rate, mutation_rate)
        animal.hunting_behaviour = np.clip(animal.hunting_behaviour, 0, 1)
        
        #
        #
        #
        #nn change!
        #
        #
        #
        
        
    def evolve_population(self):
        new_gen_flag = False
        self.population.clear() #erase the stored population
        for organism in self.environment.organisms:
            if isinstance(organism, Animal): #Check for suitable animals amongst the environments organisms
                self.population.append(organism) #append the animal to the reproducable population
        for animal in self.population:
            animal.encounter(self.population)  # Check for encounters with other fish
            if animal.encountered_animals:    
                if (animal.sex == "female") &(animal.is_ready_to_mate()):
                    partner = animal.get_mating_partner()
                    if partner:
                        animal.mate(partner, self)
                        new_gen_flag = True
        if new_gen_flag:
            self.generations_completed += 1 