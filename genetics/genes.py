from typing import Optional, Callable, Self
from enum import Enum
import math
import random
from tinydb import TinyDB, Query
from config import population_config #! should be inherited from population

# activation functions (move this)
def sigmoid(x: float): 
    return 1 / (1 + math.exp(-x))
def tanh(x: float):
    return math.tanh(x)
def relu(x: float):
    return max(0, x)
def linear(x: float):
    return x

activation_functions = [sigmoid, tanh, relu, linear]

class NodeType(Enum):
    INPUT = 1
    OUTPUT = 2
    HIDDEN = 3

class NodeGene():
    def __init__(self, id: int, type: Optional[NodeType] = None) -> None:
        self.type = type if type else NodeType.HIDDEN
        self.id = id

        if type == NodeType.INPUT:
            self.activation = linear
        else:
            self.roll_activation()

    def roll_activation(self):
        self.activation = random.choice(activation_functions)
    def __call__(self, input: float) -> float:
        return self.activation(input)
    def __eq__(self, value: Self) -> bool:
        return self.id == value.id
    def __str__(self) -> str:
        return f"id: {self.id} | type: {self.type.name} | f: {self.activation.__name__}"


class ConnectionGene():
    def __init__(self, nodes: Optional[list[NodeGene]] = None, weight: Optional[float] = None, start: Optional[NodeGene] = None, end: Optional[NodeGene] = None) -> None:
        self.weight = weight if weight else random.uniform(-1, 1)
        self.enabled = True
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
            raise ValueError("New connection needs nodes") # todo: handle this better
        
        # reorder nodes to properly identify connection
        self.reorder() # todo: could be initialized in order
        
        db = TinyDB(f"pop-{population_config['population_id']}.json")
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
        if self.start.id > self.end.id:
            self.start, self.end = self.end, self.start

    # check if any two connections are equal
    def __eq__(self, value: Self) -> bool:
        # todo: could just compare innovation numbers?
        return self.start.__eq__(value.start) and self.end.__eq__(value.end) or self.start.__eq__(value.end) and self.end.__eq__(value.start)
    # string representation of connection
    def __str__(self) -> str:
        return f"inv: {self.innovation} | enabled: {self.enabled} | {self.start.id} -> {self.end.id}"

    