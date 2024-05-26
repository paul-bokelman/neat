import unittest
import numpy as np
from uuid import uuid4
from config.configuration import Configuration
from genetics.organism import Organism
from genetics.genes import NodeGene, ConnectionGene, NodeType, sigmoid, relu

# feedforward network test cases
class TestNetwork(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        pop_config = Configuration("./config/pop1.yaml").get()

        self.nodes = [
            NodeGene(id=0, type=NodeType.INPUT),
            NodeGene(id=1, type=NodeType.INPUT),
            NodeGene(id=2, type=NodeType.INPUT),
            NodeGene(id=3, type=NodeType.OUTPUT, activation=sigmoid),
            NodeGene(id=4, type=NodeType.OUTPUT, activation=sigmoid),
            NodeGene(id=5, type=NodeType.OUTPUT, activation=sigmoid),
            NodeGene(id=6, type=NodeType.HIDDEN, activation=relu),
            NodeGene(id=7, type=NodeType.HIDDEN, activation=relu),
        ]

        genome = [
            ConnectionGene(population_name='test', nodes=self.nodes, weight=2, start=self.nodes[0], end=self.nodes[6]),
            ConnectionGene(population_name='test', nodes=self.nodes, weight=1, start=self.nodes[1], end=self.nodes[6]),
            ConnectionGene(population_name='test', nodes=self.nodes, weight=0.4, start=self.nodes[2], end=self.nodes[7]),
            ConnectionGene(population_name='test', nodes=self.nodes, weight=0.2, start=self.nodes[2], end=self.nodes[5], enabled=False),
            ConnectionGene(population_name='test', nodes=self.nodes, weight=1.3, start=self.nodes[1], end=self.nodes[3], enabled=False),
            ConnectionGene(population_name='test', nodes=self.nodes, weight=1, start=self.nodes[7], end=self.nodes[3]),
            ConnectionGene(population_name='test', nodes=self.nodes, weight=2, start=self.nodes[7], end=self.nodes[4]),
            ConnectionGene(population_name='test', nodes=self.nodes, weight=0.6, start=self.nodes[6], end=self.nodes[5]),
            ConnectionGene(population_name='test', nodes=self.nodes, weight=0.1, start=self.nodes[6], end=self.nodes[4])
        ]

        self.organism = Organism(species_id=uuid4(), config=pop_config, genome=genome,nodes=self.nodes)

        self.inputs = [0.2, 1.4, 0.7]
        i0, i1, i2 = self.inputs[0], self.inputs[1], self.inputs[2]

        h6 = relu(i0*2 + i1*1)
        h7 = relu(i2*0.4)

        o3 = sigmoid(h7*1)
        o4 = sigmoid(h6*0.1 + h7*2)
        o5 = sigmoid(h6*0.6)

        self.expected = [o3, o4, o5]

        super().__init__(methodName)

    # test the networks propagation
    def test_propagate(self):
        outputs = self.organism.phenotype().propagate(inputs=self.inputs)
        np.testing.assert_array_equal(self.expected, outputs, "Expected outputs do not match computed outputs")

if __name__ == '__main__':
    unittest.main()

