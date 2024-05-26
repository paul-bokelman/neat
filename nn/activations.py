from typing import Optional
from enum import Enum
import math
import random
from functools import partial

# all possible activation function with their implementations 
class ActivationFunctions(Enum):
    Linear = partial(lambda x: x)
    Sigmoid = partial(lambda x: 1 / (1 + math.exp(-x)))
    Tanh = partial(lambda x: math.tanh(x))
    ReLu = partial(lambda x: max(0, x))

# Over-arching activation function used in genes
class ActivationFunction:
    def __init__(self, function: Optional[ActivationFunctions] = None) -> None:
        # given a function -> just use that 
        if function is not None:
            self.function = function.value
        # no function -> randomly select one
        else:
            self.function = random.choice(list(ActivationFunctions)).value
    
    def __call__(self, x: float) -> float:
        return self.function(x)