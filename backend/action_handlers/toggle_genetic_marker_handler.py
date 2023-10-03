
from models.plant_model import PlantModel
from plants.plant import Plant

def handle_toggle_genetic_marker(action):
    plant_id = action["plant_id"]
    existing_plant_model = PlantModel.query.filter_by(id=plant_id).first()
    if existing_plant_model:
        existing_plant = Plant.from_dict(existing_plant_model.to_dict())
        existing_plant.toggle_genetic_marker()
    else:
        print(f"No plant found with id {plant_id}")
