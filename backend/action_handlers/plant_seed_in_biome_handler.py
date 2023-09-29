def handle_plant_seed_in_biome(action, game_state):
    #print the attempted action
    print("Plant Seed in Biome")
    biome_name = action["biome_name"]
    genetic_marker_cost = action["genetic_marker_cost"]
    game_state.plant_seed_in_biome(biome_name, genetic_marker_cost)
