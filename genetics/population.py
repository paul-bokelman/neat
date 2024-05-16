from typing import Callable
import random
from uuid import uuid4
from tinydb import TinyDB
from genetics.species import Species
from genetics.organism import Organism
from utils import random_exclude

class Population:
    def __init__(self, config: dict, fitness_function: Callable[[Organism], float]):
        self.population_id = config['population_id'] if 'population_id' in config else uuid4()
        self.population_size = config['population_size']
        self.db = TinyDB(f"pop-{self.population_id}.json") #? randomized db name?
        self.species: list[Species] = []
        self.fitness_function = fitness_function
        self.compatibility_config = {
            "threshold": config['compatibility']['threshold'],
            "excess_factor": config['compatibility']['excess_factor'],
            "disjoint_factor": config['compatibility']['disjoint_factor'],
            "weight_factor": config['compatibility']['weight_factor']
        }
        self.species_config = config['species']

        self.db.drop_tables() # clear db

        # create a new species, and add it to the population
        # evolve the population and redistribute the organisms into species

        initial_species = Species(self.species_config)

        # create initial population
        for _ in range(config['population_size']):
            initial_species.add(Organism(self.species_config))

        self.species.append(initial_species)

    # tournament selection -> crossover -> mutation -> speciation
    def evolve(self):
        # -------------------------------- speciation -------------------------------- #
        population: list[Organism] = []
        # todo: don't replace species entirely, maintain them

        # put all members of population in a single list and calculate fitness
        for species in self.species:
            for organism in species.organisms:
                organism.fitness = self.fitness(organism) 
                population.append(organism)

        updated_species: list[Species] = []

        # while there are still organisms that haven't been assigned to a species...
        while len(population) > 0:
            # get random "representative" organism and remove it from the population
            representative_organism_index = random.randint(0, len(population)) - 1
            representative_organism = population.pop(representative_organism_index)
            species = Species(self.species_config)
            species.add(representative_organism)

            # check genetic distance between representative and all remaining organisms in population
            for organism in population:
                genetic_distance = self.compatibility(representative_organism, organism)

                # if genetic distance between organisms is below threshold -> add to representative species
                if genetic_distance < self.compatibility_config['threshold']:
                    species.add(organism)
                    population.remove(organism)

            # add representative species to list
            updated_species.append(species)

        self.species = updated_species

        # calculate global adjusted fitness average
        global_fitness_average = 0
        for species in self.species:
            species.apply_adjusted_fitness()
            global_fitness_average += species.average_fitness

        # ----------------- tournament and crossover for each species ---------------- #
        for (index, species) in enumerate(self.species):
            allowed_offspring = species.allowed_offspring(global_fitness_average, self.population_size)
            new_organisms: list[Organism] = []

            # if only 1 organism in species, copy it n times with possible mutation
            if len(species) < 2:
                for _ in range(allowed_offspring):
                    new_organisms.append(species.get(0))
                continue

            # tournament selection for crossover candidates
            candidates: list[Organism] = []
            for _ in range(2 * allowed_offspring):
                p1_index = random.randint(0, len(species) - 1)
                participant1 = species.get(p1_index)
                p2_index = random_exclude(0, len(species) - 1, p1_index)
                participant2 = species.get(p2_index)

                # whoever has better fitness is added to candidate pool, loser is removed from species
                if(self.fitness(participant1) > self.fitness(participant2)):
                    candidates.append(participant1)
                else:
                    candidates.append(participant2)

            candidate_middle_index = int(len(candidates) / 2)

            # crossover for all pairs of candidates
            for (parent1, parent2) in zip(candidates[:candidate_middle_index], candidates[candidate_middle_index:]):
                organism = species.crossover(parent1, parent2)
                new_organisms.append(organism)

            species.organisms = new_organisms
            self.species[index] = species


    # calculate genetic distance between two organisms
    def compatibility(self, o1: 'Organism', o2: 'Organism') -> float:
        # empty genome -> distance = 0 
        if len(o1.genome) == 0 and len(o2.genome) == 0:
            return 0

        _, shared_connections, disjoint_connections, excess_connections = o1.gene_distribution(o2)
        n_excess = len(excess_connections) # number of excess genes
        n_disjoint = len(disjoint_connections) # number of disjoint genes
        avg_weight = 0 # average weight differences of shared_connections

        # check if there is at least 1 shared connection
        # todo: only enabled connections for weights!
        if len(shared_connections) != 0:
            # compute average weight differences of shared connections (i don't know if this is correct)
            for (c1, c2) in shared_connections:
                avg_weight += abs(c1.weight - c2.weight)

            avg_weight /= len(shared_connections)
        else:
            avg_weight = 0

        max_genome_size = max(len(o1.genome), len(o2.genome)) # larger genome length
        excess_factor = self.compatibility_config['excess_factor'] # excess factor
        disjoint_factor = self.compatibility_config['disjoint_factor'] # disjoint factor
        weight_factor = self.compatibility_config['weight_factor'] # weight factor
 
        distance = (n_excess * excess_factor) / max_genome_size  + (n_disjoint * disjoint_factor) / max_genome_size + avg_weight * weight_factor

        return distance
    
    # get the best preforming organism in population
    def best(self):
        best: Organism = self.species[0].get(0)
        for species in self.species:
            for organism in species.organisms:
                if organism.fitness > best.fitness:
                    best = organism
        return best

    # user defined fitness function
    def fitness(self, organism: 'Organism'):
        return self.fitness_function(organism)

    def __str__(self) -> str:
        population_str = f'Population ({self.population_id}):'
        population_str += f"\n  Species ({len(self.species)})"
        for (index, species) in enumerate(self.species):
            population_str += f'\n      ({index}) {species}'
        return population_str