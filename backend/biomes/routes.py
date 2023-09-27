from flask import jsonify, current_app

from . import biomes

@biomes.route('/biomes', methods=['GET'])
def get_biomes():
    game_state = current_app.config.get('game_state')
    if game_state is None or game_state.biomes is None:
        return jsonify({"error": "Game state or biomes not initialized"}), 400
    biomes = [biome.name for biome in game_state.biomes]
    return jsonify(biomes)
