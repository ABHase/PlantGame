from models.plant_model import PlantModel
from plants.plant import Plant
from user_auth.user_auth import fetch_upgrade_by_effect_and_user

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
            existing_plant = Plant.from_dict(existing_plant_model.to_dict())
            existing_plant.purchase_plant_part(plant_part_type)
            # Save changes to the database
        elif not upgrade:
            print(f"No upgrade found with effect {plant_part_type}")
        else:
            print(f"The upgrade for {plant_part_type} is not yet unlocked.")
    else:
        print(f"No plant found with id {plant_id}")
