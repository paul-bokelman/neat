from typing import TypedDict, cast
import yaml

OrganismConfig = TypedDict("OrganismConfig", {
    "inputs": int,
    "outputs": int,
    "mutation_chance": float,
    "structural_mutation_chance": float,
    "structural_connection_mutation_chance": float,
    "structural_connection_addition_chance": float,
    "structural_node_addition_chance": float,
    "activation_function_mutation_chance": float,
})
SpeciationConfig = TypedDict('SpeciationConfig', {
    "target_species": int,
    "threshold_step": float,
    "excess_factor": float,
    "disjoint_factor": float,
    "weight_factor": float
})

PopulationConfig = TypedDict('PopulationConfig', {
    "name": str,
    "carrying_capacity": int, 
    "speciation": SpeciationConfig, 
    "organism": OrganismConfig
})

# population configuration helper
class Configuration:
    def __init__(self, location: str) -> None:  
        self.config: PopulationConfig
        with open(location) as stream:
            try:
                self.config = cast(PopulationConfig, yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

    def get(self) -> 'PopulationConfig':
        return self.config