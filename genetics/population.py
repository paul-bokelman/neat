from typing import Callable
import random
from tinydb import TinyDB
from genetics.species import Species
from genetics.organism import Organism
from utils import random_exclude, chance
from config.configuration import PopulationConfig

# population controller for continued evolution of organisms through speciation and crossover
class Population:
    def __init__(self, config: 'PopulationConfig', fitness_function: Callable[[Organism], float]):
        self.config = config
        self.name = config.get('name')
        self.carrying_capacity = config.get('carrying_capacity')
        self.db = TinyDB(f"{self.name}-db.json")
        self.species: list[Species] = []
        self.fitness_function = fitness_function

        self.total_fitness = 0 # calculated on init and every evolution
        self.total_adjusted_fitness = 0

        # compatibility threshold and config for attaining target species
        self.compatibility_threshold = 0
        self.compatibility_threshold_step = config.get('speciation').get('threshold_step')
        self.target_species = config.get('speciation').get('target_species')

        # clear database (for need connections)
        self.db.drop_tables()

        # create a new species, and add it to the population
        # evolve the population and redistribute the organisms into species
        initial_species = Species(config=self.config)

        # create initial population
        for _ in range(self.config.get('carrying_capacity')):
            initial_species.add(Organism(species_id=initial_species.id, config=self.config))

        self.species.append(initial_species)

    # tournament selection -> crossover -> mutation -> speciation
    def evolve(self):

        # compute population fitness for this generation 
        self.compute_population_fitness()

        # adjust compatibility threshold to normalize # of species to target
        self.adjust_compatibility_threshold()

        # -------------------------------- speciation -------------------------------- #
        population: list[Organism] = []
    
        # put all members of population in a single list and calculate fitness
        for species in self.species:
            for organism in species.organisms:
                population.append(organism)

        # todo: don't replace species entirely, maintain them...
        updated_species: list[Species] = []

        # while there are still organisms that haven't been assigned to a species...
        while len(population) > 0:
            # get random "representative" organism and remove it from the population
            representative_organism_index = random.randint(0, len(population)) - 1
            representative_organism = population.pop(representative_organism_index)
            species = Species(config=self.config)
            species.add(representative_organism)

            # check genetic distance between representative and all remaining organisms in population
            for organism in population:
                genetic_distance = self.compatibility(representative_organism, organism)

                # if genetic distance between organisms is below threshold -> add to representative species
                if genetic_distance < self.compatibility_threshold:
                    species.add(organism)
                    population.remove(organism)

            # add representative species to list
            updated_species.append(species)

        self.species = updated_species

        # ------------------------- intermediate calculations ------------------------ #
        # calculate this generations total adjusted fitness (used to determine # of offspring)
        self.compute_population_adjusted_fitness_sum()
            
        # ----------------- tournament and crossover for each species ---------------- #
        for (index, species) in enumerate(self.species):
            allowed_offspring = species.allowed_offspring(pop_total_adjusted_fitness=self.total_adjusted_fitness, population_size=self.config.get('carrying_capacity'))

            new_organisms: list[Organism] = []

            # if only 1 organism in species, copy it n times with possible mutation
            if len(species) < 2:
                for _ in range(allowed_offspring):
                    new_organism = species.get(0)

                    if chance(self.config.get('organism').get('mutation_chance')):
                        new_organism.mutate()

                    new_organisms.append(new_organism)
                species.organisms = new_organisms
                self.species[index] = species
                continue

            # tournament selection for crossover candidates
            candidates: list[Organism] = []
            for _ in range(2 * allowed_offspring):
                p1_index = random.randint(0, len(species) - 1)
                participant1 = species.get(p1_index)
                p2_index = random_exclude(0, len(species) - 1, p1_index)
                participant2 = species.get(p2_index)

                # whoever has better fitness is added to candidate pool, loser is removed from species
                if(participant1.fitness > participant2.fitness):
                    candidates.append(participant1)
                else:
                    candidates.append(participant2)

            candidate_middle_index = int(len(candidates) / 2)

            # crossover for all pairs of candidates
            for (parent1, parent2) in zip(candidates[:candidate_middle_index], candidates[candidate_middle_index:]):
                organism = species.crossover(parent1, parent2)
                organism.fitness = self.fitness(organism) # in-efficient - calculating fitness on birth...
                new_organisms.append(organism)

            # todo: should check if there are no organisms
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
        excess_factor = self.config.get('speciation').get('excess_factor') # excess factor
        disjoint_factor = self.config.get('speciation').get('disjoint_factor') # disjoint factor
        weight_factor = self.config.get('speciation').get('weight_factor') # weight factor
 
        distance = (n_excess * excess_factor) / max_genome_size  + (n_disjoint * disjoint_factor) / max_genome_size + avg_weight * weight_factor

        return distance

    # compute direction step and new compatibility threshold (if target is perfect -> skip)
    def adjust_compatibility_threshold(self):

        # if current number of species is equal to desired target then skip (threshold is in a good place)
        if len(self.species) == self.target_species:
            return

        # if current number of species is higher then make it harder to split, otherwise make it easier
        if len(self.species) > self.target_species:
            self.compatibility_threshold += self.compatibility_threshold_step
        else:
            self.compatibility_threshold -= self.compatibility_threshold_step
    
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
    
    # compute the populations average adjusted fitness (per generation)
    def compute_population_adjusted_fitness_sum(self):
        self.total_adjusted_fitness = 0
        for species in self.species:
            species.apply_adjusted_fitness()
            self.total_adjusted_fitness += species.total_adjusted_fitness

    # compute the fitness for every organism in the population
    def compute_population_fitness(self):
        for species in self.species:
            for organism in species.organisms:
                organism.fitness = self.fitness(organism)

    # string representation of population
    def __str__(self, show_organisms = True) -> str:
        population_str = f"Population ({self.config.get('name')}):"
        population_str += f"\n  Total Organisms: {sum([len(s) for s in self.species])}"
        population_str += f"\n  Species ({len(self.species)})"
        for (index, species) in enumerate(self.species):
            population_str += f'\n    ({index}) {species.__str__(show_organisms=show_organisms)}'
        return population_str