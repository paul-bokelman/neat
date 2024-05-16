from typing import Optional, Callable
import random
import numpy as np
from genetics.genes import ConnectionGene, NodeGene, NodeType
from utils import chance
from uuid import UUID, uuid4

default_organism_config = { # todo: remove (should always get config from species)
    "inputs": 3, 
    "outputs": 1,
    "structural_mutation_chance": 0.3, 
    "structural_connection_mutation_chance": 0.95 
}

# Organism class (essentially genome)
class Organism:
    def __init__(self, species_id: UUID, config: Optional[dict] = None, genome: Optional[list[ConnectionGene]] = None, nodes: Optional[list[NodeGene]] = None) -> None:
        self.id = uuid4()
        self.species_id = species_id
        self.genome: list[ConnectionGene] = []
        self.nodes: list[NodeGene] = []
        self.config = config if config else default_organism_config
        self.fitness = 0.0
        self.adjusted_fitness = 0.0

        if genome and nodes:
            self.genome = genome
            self.nodes = nodes
        else:
            # create default genome with n_inputs and n_outputs
            for _ in range(self.config['inputs']):
                node = NodeGene(len(self.nodes), type=NodeType.INPUT)
                self.nodes.append(node)

            for _ in range(self.config['outputs']):
                node = NodeGene(len(self.nodes), type=NodeType.OUTPUT)
                self.nodes.append(node)

    # randomly mutate the organism's structure or connection weights
    def mutate(self):
        if chance(self.config['structural_mutation_chance']): # add new connection
            if chance(self.config['structural_connection_mutation_chance']):
                # create a new connection
                new_connection = ConnectionGene(nodes=self.nodes) #? check if connection already exists

                # check for existing connections
                for connection in self.genome:
                    if new_connection.__eq__(connection):
                        return

                self.genome.append(new_connection)
            else: # add new node (structural change)
                # create a new node
                new_node = NodeGene(id=len(self.nodes))
                self.nodes.append(new_node)

                if len(self.genome) > 0:
                    # select a random connection and disable it
                    random_connection = random.choice(self.genome)
                    random_connection.disable()

                    # connect the left side of the node back and assign decent weight
                    left_connection = ConnectionGene(start=random_connection.start, end=new_node, weight=1)

                    # connect the right side of the node forward and use previous weight
                    right_connection = ConnectionGene(start=new_node, end=random_connection.end, weight=random_connection.weight)

                    # add new connections to genome
                    self.genome.append(left_connection)
                    self.genome.append(right_connection)
                else: # if no connections just add random connection
                    new_connection = ConnectionGene(nodes=self.nodes)
                    self.genome.append(new_connection)
        else:
            # if chance hits (and there are hidden nodes) -> update random nodes activation function
            if chance(self.config['activation_function_mutation_chance']) and len(self.nodes) > (self.config['inputs'] + self.config['outputs']): 
                temp_nodes = self.nodes.copy()
                random.shuffle(temp_nodes) # randomly shuffle nodes

                # find first hidden node and re-roll it's activation
                for (index, node) in enumerate(temp_nodes):
                    if node.type == NodeType.HIDDEN:
                        node.roll_activation()
                        temp_nodes[index] = node
                        break
                
                self.nodes = temp_nodes
            elif len(self.genome) > 0: # if at least one connection -> randomly change random connection weight
                random_connection = random.choice(self.genome)
                random_connection.randomize_weight(factor=0.2)
                # random_connection.nudge_weight() # incremental changes (to preserve importance?)
            

    # Phenotype is network of nodes and connections (returns function)
    def phenotype(self) -> Callable[[list[float]], list[float]]:
        connections = self.genome.copy()
        def network(inputs: list[float]) -> list[float]:
            output = []
            return output
        return network
    
    # return shared nodes and shared, disjoint, excess connections between organisms
    def gene_distribution(self, other_organism: 'Organism'):
        nodes = [] # collect larger organism's nodes
        shared_connections: list[tuple[ConnectionGene, ConnectionGene]] = [] # tuple of connections for children random selection
        disjoint_connections: list[ConnectionGene] = [] # a connection that 1 organism has that the other doesn't
        excess_connections: list[ConnectionGene] = [] # extra connections from larger organism

        larger_organism = self if len(self.genome) > len(other_organism.genome) else other_organism
        smaller_organism= other_organism if len(self.genome) > len(other_organism.genome) else self

        higher_node_organism = self if len(self.nodes) > len(other_organism.nodes) else other_organism
        
        # add nodes from larger organism
        nodes = higher_node_organism.nodes

        mutable_smaller_organism_genome = smaller_organism.genome.copy()

        # find largest innovation number in genes
        smaller_organism_innovations = [c.innovation for c in smaller_organism.genome]
        largest_smaller_genome_innovation = max(smaller_organism_innovations) if len(smaller_organism_innovations) > 0 else 0

        # find shared, excess, and disjoint genes
        for c1 in larger_organism.genome: 
            # check if both genomes contain same connection (shared)
            c2 = next((c for c in mutable_smaller_organism_genome if c1 == c), None)
            if isinstance(c2, ConnectionGene): 
                shared_connections.append((c1, c2))

                # remove connection from smaller genome (smaller search space & leftovers -> disjoint)
                mutable_smaller_organism_genome.remove(c1) 
            # check if excess gene
            elif c1.innovation > largest_smaller_genome_innovation:
                excess_connections.append(c1)
            # if not excess or shared -> disjoint
            else:
                disjoint_connections.append(c1)

        # disjoint connections are combination of leftover genes from smaller genome and disjoints from larger genome
        disjoint_connections = disjoint_connections + mutable_smaller_organism_genome

        return (nodes, shared_connections, disjoint_connections, excess_connections)
    
    # pretty print organism
    def __str__(self, short: Optional[bool] = False) -> str:
        organism_str = f"Organism ({self.id}): nodes ({len(self.nodes)}) | connections ({len(self.genome)})"

        if short:
            return organism_str

        organism_str += f"\n  Nodes ({len(self.nodes)}):"
        for node in self.nodes:
            organism_str +=f"\n    {node}"
        organism_str += f"\n  Connections ({len(self.genome)}):"
        for connection in self.genome:
            organism_str += f"\n    {connection}"

        return organism_str