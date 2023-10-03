from models.plant_model import PlantModel
from plants.plant import Plant


def handle_toggle_sugar(action):
    plant_id = action["plant_id"]  # Assuming you have plant_id in the action

    # Fetch the plant from the database
    existing_plant_model = PlantModel.query.filter_by(id=plant_id).first()

    if existing_plant_model:
        # Convert the PlantModel to a Plant object
        existing_plant = Plant.from_dict(existing_plant_model.to_dict())

        # Toggle sugar production and save
        existing_plant.toggle_sugar_production()
    else:
        print(f"No plant found with id {plant_id}")
