def handle_toggle_genetic_marker(action, game_state):
    plant = game_state.biomes[action["biomeIndex"]].plants[action["plantIndex"]]
    plant.toggle_genetic_marker()