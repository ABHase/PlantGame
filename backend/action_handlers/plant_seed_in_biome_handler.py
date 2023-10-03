import uuid
from game_state.plants_config import INITIAL_PLANT_CONFIG
from models.plant_model import PlantModel
from models.biome_model import BiomeModel
from user_auth.user_auth import fetch_global_state_from_db, save_global_state_to_db, save_new_plant_to_db

def handle_plant_seed_in_biome(action):
    biome_id = action["biome_id"]
    genetic_marker_cost = 1 # For now, this could be a hardcoded number

    # Fetch the biome to get the user_id
    existing_biome_model = BiomeModel.query.filter_by(id=biome_id).first()
    if existing_biome_model:
        user_id = existing_biome_model.user_id

        # Fetch the global state to get the current number of seeds and genetic markers
        global_state_model = fetch_global_state_from_db(user_id)
        seeds = global_state_model.seeds
        genetic_markers = global_state_model.genetic_markers

        if seeds > 0 and genetic_markers >= genetic_marker_cost:
            save_new_plant_to_db(user_id, biome_id)
            
            # Update the global state
            global_state_model.seeds -= 1
            global_state_model.genetic_markers -= genetic_marker_cost
            save_global_state_to_db(user_id, global_state_model)

            print("Seed successfully planted.")
        else:
            print("Failed to plant seed.")
    else:
        print(f"No biome found with id {biome_id}")
