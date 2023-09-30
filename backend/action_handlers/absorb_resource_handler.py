# absorb_resource_handler.py

def handle_absorb_resource(action, game_state):
    biomeIndex = action.get('biomeIndex')
    plantIndex = action.get('plantIndex')
    resourceType = action.get('resourceType')  # 'water' or 'sunlight'
    amount = action.get('amount')  # Amount to absorb

    biome = game_state.biomes[biomeIndex]
    plant = biome.plants[plantIndex]

    if resourceType == 'water':
        if biome.has_enough_ground_water(amount):
            plant.absorb_resource(resourceType, amount)
            biome.decrease_ground_water_level(amount)
        else:
            print("Not enough water in the biome to absorb.")
    else:
        plant.absorb_resource(resourceType, amount)
