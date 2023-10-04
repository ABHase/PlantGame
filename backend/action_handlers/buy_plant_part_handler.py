from plants.part_cost_config import PARTS_COST_CONFIG
from models.plant_model import PlantModel
from plants.plant import Plant
from user_auth.user_auth import fetch_upgrade_by_effect_and_user, save_single_plant_to_db

def handle_buy_plant_part(action):
    plant_id = action["plant_id"]
    plant_part_type = action["partType"]

    # Fetch the plant from the database
    existing_plant_model = PlantModel.query.filter_by(id=plant_id).first()

    if existing_plant_model:
        user_id = existing_plant_model.user_id  # Get user_id from the plant model

        # Fetch the upgrade from the database
        upgrade = fetch_upgrade_by_effect_and_user(plant_part_type, user_id)

        if upgrade and upgrade.unlocked:
            cost = PARTS_COST_CONFIG.get(plant_part_type, 0)
            if cost == 0:
                print(f"Invalid plant part type: {plant_part_type}")
                return

            if plant_part_type == 'resin' and existing_plant_model.resin >= existing_plant_model.leaves:
                print("Cannot purchase more resin than the number of leaves.")
                return

            if existing_plant_model.sugar >= cost:
                setattr(existing_plant_model, plant_part_type, getattr(existing_plant_model, plant_part_type) + 1)
                existing_plant_model.sugar -= cost
                save_single_plant_to_db(existing_plant_model)
            else:
                print(f"Not enough sugar to purchase {plant_part_type}.")
        elif not upgrade:
            print(f"No upgrade found with effect {plant_part_type}")
        else:
            print(f"The upgrade for {plant_part_type} is not yet unlocked.")
    else:
        print(f"No plant found with id {plant_id}")
