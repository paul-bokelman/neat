from typing import Optional, Self, Callable
from enum import Enum
import random
from tinydb import TinyDB, Query
from nn.activations import ActivationFunction, ActivationFunctions

# node type identifier
class NodeType(Enum):
    INPUT = 1
    OUTPUT = 2
    HIDDEN = 3

# node gene for organism (activation functions)
class NodeGene:
    def __init__(self, id: int, type: Optional[NodeType] = None, activation: Optional[ActivationFunction] = None) -> None:
        self.type = type if type else NodeType.HIDDEN
        self.id = id
        self.value: Optional[float] = None

        # input node activation is always linear
        if type == NodeType.INPUT:
            self.activation = ActivationFunction(ActivationFunctions.Linear)
        elif activation:
            self.activation = activation
        else:
            self.roll_activation()

    # randomly choose a different activation function
    def roll_activation(self):
        self.activation = ActivationFunction()

    # apply activation function to input value and assign to node
    def activate(self, input: float):
        self.value = self.activation(input)

    # reset the nodes value
    def clear(self):
        self.value = None

    # directly call the activation function for this node
    def __call__(self, input: float) -> float:
        return self.activation(input)
    
    # check if any two nodes are equal (compare unique id)
    def __eq__(self, node: Self) -> bool:
        return self.id == node.id
    
    # string representation of node
    def __str__(self) -> str:
        return f"id: {self.id} | type: {self.type.name} | f: {self.activation} | Value: {self.value}"

# connection gene for organisms genomes (connections between nodes)
class ConnectionGene:
    def __init__(self, population_name: str, nodes: Optional[list[NodeGene]] = None, weight: Optional[float] = None, start: Optional[NodeGene] = None, end: Optional[NodeGene] = None, enabled: bool = True) -> None:
        self.weight = weight if weight else random.uniform(-1, 1)
        self.enabled = enabled
        self.innovation: int = 0

        if start and end:
            self.start = start
            self.end = end
        elif nodes:
            temp_nodes = nodes.copy()
            random.shuffle(temp_nodes)

            # randomly choose starting node
            self.start = temp_nodes.pop(random.randint(0, len(nodes) - 1))

            # choose node with different type (ensure they aren't in the same layer)
            for node in temp_nodes:
                if node.type == self.start.type:
                    continue
                self.end = node
                break
        else:
            raise ValueError("New connection needs nodes")
        
        # reorder nodes to properly identify connection
        self.reorder() #? could be initialized in order
        
        #? I don't like receiving population name like this...
        db = TinyDB(f"{population_name}-db.json")
        Innovations = Query()

        # check if connection exists
        connection_query = db.search(Innovations.connection == f"{self.start.id}-{self.end.id}")

        # if connection exists, fetch innovation number and assign it to connection
        if len(connection_query) > 0:
            self.innovation = connection_query[0]['innovation']
        else:
            # if connection doesn't exist, assign new innovation number and insert it into db
            connection_count = db.count(Innovations.connection.exists())
            if connection_count > 0:
                self.innovation = connection_count
            db.insert({'innovation': self.innovation, 'connection': f"{self.start.id}-{self.end.id}"})
    
    # disable connection
    def disable(self):
        self.enabled = False

    # enable connection
    def enable(self):
        self.enabled = True

    # nudge weight in random direction (doesn't completely override weight)
    def nudge_weight(self, factor: Optional[float] = None): #todo: unused
        direction = -1 if random.randint(0, 1) == 0 else 1
        self.weight += direction * (factor if factor else 1)

    # randomize value of weight, optionally scale uniform value
    def randomize_weight(self, factor: Optional[float] = None):
        self.weight =  random.uniform(-1, 1) * (factor if factor else 1)
    
    # reorder nodes, if start node is greater than end node, swap them
    def reorder(self):
        # if end is of type input then swap (input is always start)
        if self.end.type == NodeType.INPUT:
            self.start, self.end = self.end, self.start
        # if start is of type output then swap (output is always end)
        elif self.start.type == NodeType.OUTPUT:
            self.start, self.end = self.end, self.start
        # if both nodes are hidden then numerically order
        elif self.start.type == NodeType.HIDDEN and self.end.type == NodeType.HIDDEN and self.start.id > self.end.id:
            self.start, self.end = self.end, self.start

    # check if connection is connected to node
    def is_connected_to(self, node: 'NodeGene'):
        return self.start == node or self.end == node

    # check if any two connections are equal
    def __eq__(self, connection: Self) -> bool:
        #? compare innovation numbers?
        return self.start == connection.start and self.end == connection.end or self.start == connection.end and self.end == connection.start

    # string representation of connection
    def __str__(self) -> str:
        return f"inv: {self.innovation} | enabled: {self.enabled} | {self.start.id} -> {self.end.id} | W: {self.weight}"

    