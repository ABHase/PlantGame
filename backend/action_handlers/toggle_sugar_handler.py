def handle_toggle_sugar(action, game_state):
    plant = game_state.biomes[action["biomeIndex"]].plants[action["plantIndex"]]
    plant.toggle_sugar_production()