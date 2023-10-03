from models.plant_model import PlantModel
from user_auth.user_auth import fetch_global_state_from_db, save_global_state_to_db, save_single_plant_to_db

def handle_purchase_seed(action):
    plant_id = action["plant_id"]
    cost = 10  # This could also come from a config file

    # Fetch the plant from the database
    existing_plant_model = PlantModel.query.filter_by(id=plant_id).first()

    if existing_plant_model:
        user_id = existing_plant_model.user_id  # Get user_id from the plant model

        # Fetch the global state to get the current number of seeds
        global_state_model = fetch_global_state_from_db(user_id)
        seeds = global_state_model.seeds

        if existing_plant_model.sugar >= cost:
            # Subtract the sugar cost and add a seed
            existing_plant_model.sugar -= cost
            global_state_model.seeds += 1

            # Save changes to the database
            save_single_plant_to_db(existing_plant_model)
            save_global_state_to_db(user_id, global_state_model)

            print("Seed successfully purchased.")
        else:
            print("Not enough sugar to purchase a seed.")
    else:
        print(f"No plant found with id {plant_id}")
