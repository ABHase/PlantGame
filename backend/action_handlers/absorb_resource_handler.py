# absorb_resource_handler.py

def handle_absorb_resource(action, game_state):
    biomeIndex = action.get('biomeIndex')
    plantIndex = action.get('plantIndex')
    resourceType = action.get('resourceType')  # 'water' or 'sunlight'
    amount = action.get('amount')  # Amount to absorb

    plant = game_state.biomes[biomeIndex].plants[plantIndex]
    plant.absorb_resource(resourceType, amount)
