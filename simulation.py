import random
from config.configuration import Configuration
from genetics.population import Population
from genetics.organism import Organism
from utils import chance

generations = 10

pop_config = Configuration("./config/pop1.yaml").get()
# pop2_config = Configuration("./config/pop2.yaml").get()

# only positive values... if all members have fitness of 0 -> division by zero..
def fitness(organism: 'Organism'):
    if organism.fitness == 0:
        organism.fitness = random.uniform(1, 3)
    else: 
        if chance(0.2):
            organism.fitness += random.uniform(0, 1)
    # only positive values...
    return organism.fitness

pop = Population(pop_config, fitness)

for i in range(generations):
    pop.evolve()

out = pop.species[0].organisms[0].phenotype().propagate([1.2, 3.4, 0.2])
