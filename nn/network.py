from genetics.genes import NodeGene, ConnectionGene, NodeType

# organism phenotype
class FeedForwardNetwork:
    # store nodes and connections for propagation
    def __init__(self, n_inputs: int, nodes: list[NodeGene], connections: list[ConnectionGene]) -> None:
        self.n_inputs = n_inputs
        self.nodes = nodes
        self.enabled_connections = [c for c in connections if c.enabled]
    
    # recursively compute output values
    def propagate(self, inputs: list[float]) -> list[float]:

        # check if correct number of given inputs
        assert len(inputs) == self.n_inputs, "Given inputs must match number of input nodes"

        # clear all node values before computation
        self.__clear_nodes()

        # assign given values to input nodes
        for (index, input) in enumerate(inputs):
            for node in self.nodes:
                if node.id == index:
                    node.activate(input)

        outputs = []
 
        # compute the value of each output node
        for node in self.nodes:
            if node.type == NodeType.OUTPUT:
                self.__compute_root(node=node)
                outputs.append(node.value)

        return outputs

    # compute the activated value of a root (node)
    def __compute_root(self, node: NodeGene):

        # if the node has a value -> terminate recursion
        if node.value is not None:
            return
        
        # list of branches to compute value for activation
        branches: list[ConnectionGene] = []

        # find all immediate branches of root (children)
        for connection in self.enabled_connections:
            if connection.end == node:
                branches.append(connection)

        # the sum of all branch start nodes and their connection weights
        branches_sum = 0.0

        # compute branch sum recursively
        for branch in branches:
            # compute the value of this branches start node value
            self.__compute_root(branch.start)

            # ensure branch value isn't None and compute product of weight and previous activation
            assert branch.start.value is not None, "branch start node value shouldn't be None"
            branches_sum += branch.weight * branch.start.value

        # get computed activation value for this node
        node.activate(branches_sum)

    # clear the values for every node
    def __clear_nodes(self):
        for node in self.nodes:
            node.clear()