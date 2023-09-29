def handle_purchase_seed(action, game_state):
    print("Inside handle_purchase_seed")
    biomeIndex = action["biomeIndex"]
    plantIndex = action["plantIndex"]
    cost = action["cost"]
    plant = game_state.biomes[biomeIndex].plants[plantIndex]
    print(f"Calling purchase_seed_using_plant with plant_id: {plant.id}, cost: {cost}")
    result = game_state.purchase_seed_using_plant(plant.id, cost)
    print(f"Result of purchase: {result}")
