# from genetics.organism import Organism
# from genetics.genes import NodeType
from genetics.population import Population
from genetics.organism import Organism
from config import population_config
import random


def fitness(organism: 'Organism'):
    return random.uniform(-10, 10)

pop = Population(population_config, fitness)

for _ in range(10):
    pop.evolve()

print(pop)

# for organism in pop.species[0].organisms:
#     print(organism)