import random

# probabilistically return true
def chance(probability: float):
   return random.random() < probability 

# randomly choose an integer in the range whilst excluding given integers 
def random_exclude(lower: int = 0 , upper: int = 0, *exclude):
  exclude = set(exclude)
  ri = random.randint(lower, upper)
  return random_exclude(lower, upper, *exclude) if ri in exclude else ri 