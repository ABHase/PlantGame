from ..models.plant_model import PlantModel
from ..user_auth.user_auth import save_single_plant_to_db  # Import the function to save a plant to the database

def handle_toggle_sugar(action):
    plant_id = action["plant_id"]  # Assuming you have plant_id in the action

    # Fetch the plant from the database
    existing_plant_model = PlantModel.query.filter_by(id=plant_id).first()

    if existing_plant_model:
        # Toggle sugar production directly on the model
        existing_plant_model.is_sugar_production_on = not existing_plant_model.is_sugar_production_on

        # Save the updated model to the database
        save_single_plant_to_db(existing_plant_model)
    else:
        print(f"No plant found with id {plant_id}")
