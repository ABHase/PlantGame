def handle_buy_plant_part(action, game_state):
    user_id = action.get('user_id')
    biomeIndex = action.get('biomeIndex')
    plantIndex = action.get('plantIndex')
    partType = action.get('partType')  # 'roots' or 'leaves'
    cost = action.get('cost')  # You can also dynamically determine this based on partType

    plant = game_state.biomes[biomeIndex].plants[plantIndex]
    plant.purchase_plant_part(partType, cost)