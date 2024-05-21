from genetics.population import Population
from genetics.organism import Organism
from config import population_config
import random
from utils import chance

generations = 10

# only positive values... if all members have fitness of 0 -> division by zero..
def fitness(organism: 'Organism'):
    if organism.fitness == 0:
        organism.fitness = random.uniform(1, 3)
    else: 
        if chance(0.2):
            organism.fitness += random.uniform(0, 1)
    # only positive values...
    return organism.fitness

pop = Population(population_config, fitness)

for i in range(generations):
    pop.evolve()

print(pop.__str__(show_organisms=False))