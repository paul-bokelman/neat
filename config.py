# each population has different config
population_config = {
    "population_size": 10,
    "population_id": "unique-id",

    "species_target": 10, # target number of species in any given generation
    "threshold_step": 0.5, # reduction step towards target number of species

    # speciation division config
    "compatibility":{
        "threshold": 2, # compatibility distance to declare different species 
        "excess_factor": 1.0, 
        "disjoint_factor": 1.0,
        "weight_factor": 1.0
    },
    
    # species specific config (organism)
    "species": {
        "inputs": 3, # number of sensors (inputs for nn)
        "outputs": 1, # number of outputs for nn
        "mutation_chance": 0.2, # chance for mutation to occur
        "structural_mutation_chance": 0.3, # given mutation -> chance that structural mutation occurs given
        "structural_connection_mutation_chance": 0.95, # given structural mutation -> chance that connection is added, otherwise add node
        "activation_function_mutation_chance": 0.4 # given regular mutation -> chance to update a nodes activation function
    }
}