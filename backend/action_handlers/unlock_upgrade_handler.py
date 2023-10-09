from ..user_auth.models import UpgradeModel
from ..user_auth.user_auth import fetch_global_state_from_db, save_global_state_to_db, initialize_new_biome
from math import round

def handle_unlock_upgrade(action):
    upgrade_id = action["upgrade_id"]

    # Fetch the upgrade from the database
    existing_upgrade_model = UpgradeModel.query.filter_by(id=upgrade_id).first()

    if existing_upgrade_model:
        user_id = existing_upgrade_model.user_id  # Get user_id from the upgrade model

        # Fetch the global state to get the current number of genetic markers
        global_state_model = fetch_global_state_from_db(user_id)
        genetic_markers = global_state_model.genetic_markers
        cost_modifier = global_state_model.cost_modifier

        

        cost = existing_upgrade_model.cost  # Get the cost from the upgrade model
        # Modify the cost based on the global cost modifier
        adjusted_cost = cost * (1 + cost_modifier)  # Adding 1 because base is 100% (or 1.0)
        adjusted_cost = round(adjusted_cost)

        secondary_cost = existing_upgrade_model.secondary_cost
        secondary_resource = existing_upgrade_model.secondary_resource

        # Check if player has enough of the primary and secondary resource
        if genetic_markers >= adjusted_cost and (not secondary_resource or getattr(global_state_model, secondary_resource) >= secondary_cost):
            if not existing_upgrade_model.unlocked:
                # Unlock the upgrade
                existing_upgrade_model.unlocked = True

                # Subtract the primary resource cost
                global_state_model.genetic_markers -= adjusted_cost

                upgrade_cost_modifier = existing_upgrade_model.cost_modifier
                if upgrade_cost_modifier:
                    global_state_model.cost_modifier += upgrade_cost_modifier

                    # Subtract the secondary resource cost if it exists
                if secondary_resource:
                    setattr(global_state_model, secondary_resource, getattr(global_state_model, secondary_resource) - secondary_cost)

                # Save changes to the database
                save_global_state_to_db(user_id, global_state_model)

                # Additional logic to initialize new biomes or plant parts
                if existing_upgrade_model.type == "biome":
                    initialize_new_biome(user_id, existing_upgrade_model.effect)
                print("Upgrade successfully unlocked.")
            else:
                print("Upgrade already unlocked.")
        else:
            print("Not enough resources to unlock this upgrade.")
    else:
        print(f"No upgrade found with id {upgrade_id}")
