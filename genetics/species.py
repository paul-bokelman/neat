from uuid import uuid4
from genetics.organism import Organism
from utils import chance, random_exclude

class Species:
    def __init__(self, config: dict):
        self.id = uuid4() # could just increment id...
        self.config = config
        self.organisms: list[Organism] = [] # members of species

        # fitness for species
        self.average_fitness = 0.0
        self.total_adjusted_fitness = 0.0
        self.total_fitness = 0.0
        self.average_adjusted_fitness = 0.0
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
        total_fitness = 0
        total_adjusted_fitness = 0
        n_organisms = len(self.organisms)
        for organism in self.organisms:
            organism.adjusted_fitness = organism.fitness / n_organisms
            total_fitness += organism.fitness
            total_adjusted_fitness+= organism.adjusted_fitness

        self.average_fitness = total_fitness / n_organisms
        self.average_adjusted_fitness = total_adjusted_fitness / n_organisms
        self.total_fitness = total_fitness
        self.total_adjusted_fitness = total_adjusted_fitness

    # calculate number of allowed offspring based on average fitness against population
    def allowed_offspring(self, pop_total_adjusted_fitness, population_size):
        relative_fitness_proportion = self.total_adjusted_fitness / pop_total_adjusted_fitness
        number_of_offspring = relative_fitness_proportion * population_size

        return int(round(number_of_offspring))

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
    
    def __str__(self, show_organisms = False, short_organisms = True):
        species_str = f'Species ({self.id}): organisms ({len(self.organisms)}) | avg fit: {self.average_fitness} | adj sum: {self.total_adjusted_fitness}'
        if show_organisms:
            for o in self.organisms:
                species_str += f'\n      {o.__str__(short=short_organisms)}'

        return species_str