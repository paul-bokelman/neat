# each population has different config
population_config = {
    "population_size": 50, # initial and max population size
    "population_id": "rD594E", # random and unique database id

    "target_species": 7, # target number of species in any given generation (can't be larger than population size)
    "threshold_step": 1, # reduction step towards target number of species

    # speciation division config
    "compatibility":{
        "excess_factor": 1.0, # how much the excess genes affect compatibility
        "disjoint_factor": 1.0,  # how much the disjoint genes affect compatibility
        "weight_factor": 1.0  # how much the sum of differences in connections affect compatibility
    },
    
    # species specific config (organism)
    "species": {
        "inputs": 3, # number of sensors (inputs for nn)
        "outputs": 1, # number of outputs for nn
        "mutation_chance": 0.2, # chance for mutation to occur
        "structural_mutation_chance": 0.3, # given mutation -> chance that structural mutation occurs given
        "structural_connection_mutation_chance": 0.70, # given structural mutation -> chance that connection is added, otherwise add node
        "structural_connection_addition_chance": 0.7, # given structural connection mutation -> chance that a connection is added instead of removed
        "structural_node_addition_chance": 0.7, # given structural node mutation -> chance that a node is added instead of removed
        "activation_function_mutation_chance": 0.4 # given regular mutation -> chance to update a nodes activation function
    }
}