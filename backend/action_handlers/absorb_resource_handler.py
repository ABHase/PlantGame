from models.plant_model import PlantModel
from models.biome_model import BiomeModel
from user_auth.user_auth import save_single_plant_to_db, save_single_biome_to_db  # Import the functions to save to the database

def handle_absorb_resource(action):
    plant_id = action["plant_id"]
    resource_type = action["resourceType"]
    amount = action["amount"]

    # Fetch the plant from the database
    existing_plant_model = PlantModel.query.filter_by(id=plant_id).first()
    if not existing_plant_model:
        print(f"No plant found with id {plant_id}")
        return

    # Fetch the corresponding biome from the database
    existing_biome_model = BiomeModel.query.filter_by(id=existing_plant_model.biome_id).first()
    if not existing_biome_model:
        print(f"No biome found with id {existing_plant_model.biome_id}")
        return

    # Handle resource absorption
    if resource_type == 'water':
        max_water_capacity = existing_plant_model.vacuoles * 100
        if existing_plant_model.water + amount > max_water_capacity:
            print("Exceeds max water capacity.")
            return

        if existing_biome_model.ground_water_level >= amount:
            existing_plant_model.water += amount
            existing_biome_model.ground_water_level -= amount

            # Save changes to the database
            save_single_plant_to_db(existing_plant_model)
            save_single_biome_to_db(existing_biome_model)
        else:
            print("Not enough water in the biome to absorb.")
    else:
        setattr(existing_plant_model, resource_type, getattr(existing_plant_model, resource_type) + amount)
        
        # Save changes to the database
        save_single_plant_to_db(existing_plant_model)
