from models.plant_model import PlantModel
from models.biome_model import BiomeModel  # Assuming you have a BiomeModel
from plants.plant import Plant
from biomes.biome import Biome  # Assuming you have a Biome class

def handle_absorb_resource(action):
    plant_id = action["plant_id"]
    resource_type = action["resourceType"]
    amount = action["amount"]

    # Fetch the plant from the database
    existing_plant_model = PlantModel.query.filter_by(id=plant_id).first()
    if not existing_plant_model:
        print(f"No plant found with id {plant_id}")
        return

    existing_plant = Plant.from_dict(existing_plant_model.to_dict())

    # Fetch the corresponding biome from the database
    existing_biome_model = BiomeModel.query.filter_by(id=existing_plant.biome_id).first()
    if not existing_biome_model:
        print(f"No biome found with id {existing_plant.biome_id}")
        return

    existing_biome = Biome.from_dict(existing_biome_model.to_dict())

    # Handle resource absorption
    if resource_type == 'water':
        if existing_biome.has_enough_ground_water(amount):
            existing_plant.absorb_resource(resource_type, amount)
            existing_biome.decrease_ground_water_level(amount)  # This should also save the biome to the DB
        else:
            print("Not enough water in the biome to absorb.")
    else:
        existing_plant.absorb_resource(resource_type, amount)
