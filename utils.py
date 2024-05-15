from typing import Optional
import random

def chance(probability: float):
   return random.random() < probability 

def random_exclude(lower: int = 0 , upper: int = 0, *exclude):
  exclude = set(exclude)
  ri = random.randint(lower, upper)
  return random_exclude(lower, upper, *exclude) if ri in exclude else ri 