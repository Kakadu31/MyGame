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
        
        self.original_image = image        
        self.image = self.original_image.copy() 
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.velocity_magnitude = random.randint(0,1)
        self.velocity_angle = random.randint(-3,3)
        #self.velocity = (0,0)
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
        self.acceleration = 1
        self.encountered_animals = []
        
        self.encounter_distance_threshold = 2*environment.cell_size
        self.procreation_age = 0
        self.pregnancy_term = 120
        self.pregnancy_time = 0
        self.offspring = None
        
    def update(self, dt):
        pass
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
    #--------------------
    #------Movement------  
    #-------------------- 
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

         
    def check_boundaries(self):
        self.rect.x = np.clip(self.rect.x, 10, self.environment.width - 11)
        self.rect.y = np.clip(self.rect.y, 10, self.environment.height - 11)  
        
    def move(self, dt):
        #detect algae returns a tuple of the distance and angle of each algae
        detected_algae = self.detect_algae()
        #print(detected_algae)
        # Construct inputs for the neural network with detected algae positions
        inputs = [self.velocity_magnitude, self.velocity_angle]
        for i in range(int((self.nn_input_size-2)/2)):
            if i < len(detected_algae):
                inputs += detected_algae[i]
            else:
                inputs += [0, 0]  # Placeholder for missing algae
        #self.velocity = self.neural_network.feedforward(np.array(inputs))
        new_velocity_magnitude, new_velocity_angle = self.neural_network.feedforward(np.array(inputs))

        # Smoothly adjust the velocity and angle
        self.velocity_magnitude += (new_velocity_magnitude - self.velocity_magnitude) * self.acceleration
        self.velocity_magnitude = max(0, self.velocity_magnitude)
        if not math.isnan(new_velocity_angle):
            self.velocity_angle += (new_velocity_angle - self.velocity_angle) * 1/(self.weight*100)

        # Update fish position based on the velocity vector
        dx = self.velocity_magnitude * math.cos(self.velocity_angle)
        dy = self.velocity_magnitude * math.sin(self.velocity_angle)  # -dy because y-axis is inverted
        self.rect.x += dx*dt*self.speed
        self.rect.y += dy *dt*self.speed
        
        if not math.isnan(dx) and not math.isnan(dy) and (dx != 0 or dy != 0):
            # Calculate the angle of the new velocity vector and update the fish's rotation if necessary
            change_angle = math.atan2(dy, dx)
            if not math.isclose(self.angle, change_angle, abs_tol=0.1):
                self.image = pygame.transform.rotate(self.original_image, self.angle-int(math.degrees(change_angle)))
                self.angle = change_angle
                self.rect = self.image.get_rect(center=self.rect.center)
        
   
    #--------------------
    #------Detection------  
    #--------------------   
    
    def encounter(self, other_animal_population):
        # Iterate through other fish and check distances
        self.encountered_animals = []  # Clear the list of encountered fish
        for other_animal in other_animal_population:
            if self != other_animal:  # Exclude self
                distance = np.linalg.norm(np.array([self.rect.x, self.rect.y]) - np.array([other_animal.rect.x, other_animal.rect.y]))
                if distance < self.encounter_distance_threshold:
                    self.encountered_animals.append(other_animal)

    
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
    
    def detect_algae(self):
        detected_algae = []
        for organism in self.environment.organisms:
            if (isinstance(organism, Algae)):
                if self.point_in_polygon(organism.rect.center, self.fov_vertices):
                    # Calculate distance between the fish and the algae
                    dx = organism.rect.centerx - self.rect.centerx
                    dy = organism.rect.centery - self.rect.centery
                    distance = math.sqrt(dx ** 2 + dy ** 2)
                    
                    # Calculate angle between the fish and the algae
                    angle = math.atan2(-dy, dx)
                    
                    detected_algae.append((distance, angle))
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
    
    #--------------------
    #------Mating------  
    #--------------------            
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

    def is_ready_to_mate(self):
        if (self.age >= self.procreation_age)&(self.pregnancy_time == 0):
            return True
        else:            
            return False
        
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