from typing import Optional
import math
import random
from uuid import uuid4
from genetics.organism import Organism
from genetics.genes import ConnectionGene
from utils import chance,random_exclude

default_species_config = {
    "inputs": 3, 
    "outputs": 1,
    "tournament_proportion": 0.8,
    "mutation_chance": 0.2, 
    "structural_mutation_chance": 0.3,
    "structural_connection_mutation_chance": 0.95
}

class Species:
    def __init__(self, config: dict):
        self.id = uuid4() # could just increment id...
        self.config = config if config else default_species_config
        self.organisms: list[Organism] = [] # members of species
        self.average_fitness = 0.0
        # self.generations_since_improvement = 0 # todo: implement penalization (prevent bloat)

    # crossover 2 organisms and produce a single organism
    def crossover(self, o1: 'Organism', o2: 'Organism') -> 'Organism':
        nodes, shared_connections, disjoint_connections, excess_connections = o1.gene_distribution(o2)

        child_genome = disjoint_connections + excess_connections

        # randomly assign shared connections to each child
        for (c1, c2) in shared_connections:
            if chance(0.5):
                child_genome.append(c1)
            else:
                child_genome.append(c2)

        child = Organism(self.id, self.config, genome=child_genome, nodes=nodes)

        # random chance of mutation 
        if chance(self.config['mutation_chance']):
            child.mutate()

        #? would be nice to just append directly to this array but I think this is easier...
        return child

    # apply adjusted fitness (fitness relative to species) to all organisms in species and find average adjusted fitness
    def apply_adjusted_fitness(self):
        fitness_sum = 0
        n_organisms = len(self.organisms)
        for organism in self.organisms:
            organism.adjusted_fitness = organism.fitness / n_organisms
            fitness_sum += organism.fitness

        self.average_fitness = fitness_sum / n_organisms

    # calculate number of allowed offspring based on average fitness against population
    def allowed_offspring(self, global_fitness_avg, population_size):
        # probabilistically round allowed offspring up or down 
        #? is this correct?
        return int(math.floor((self.average_fitness / global_fitness_avg) * population_size + random.random()))

    def add(self, organism):
        self.organisms.append(organism)

    def get(self, index):
        return self.organisms[index]
    
    def remove(self, index):
        self.organisms.pop(index)

    def get_random(self, *exclude):
        return self.get(random_exclude(0, len(self.organisms) - 1, exclude))

    def __len__(self):
        return len(self.organisms)
    
    def __str__(self):
        return f'Species ({self.id}): organisms ({len(self.organisms)})'