from ..user_auth.models import UpgradeModel
from ..user_auth.user_auth import fetch_global_state_from_db, save_global_state_to_db, initialize_new_biome

def handle_unlock_upgrade(action):
    upgrade_id = action["upgrade_id"]

    # Fetch the upgrade from the database
    existing_upgrade_model = UpgradeModel.query.filter_by(id=upgrade_id).first()

    if existing_upgrade_model:
        user_id = existing_upgrade_model.user_id  # Get user_id from the upgrade model

        # Fetch the global state to get the current number of genetic markers
        global_state_model = fetch_global_state_from_db(user_id)
        genetic_markers = global_state_model.genetic_markers

        cost = existing_upgrade_model.cost  # Get the cost from the upgrade model

        if genetic_markers >= cost:
            if not existing_upgrade_model.unlocked:
                # Unlock the upgrade
                existing_upgrade_model.unlocked = True

                # Subtract the cost
                global_state_model.genetic_markers -= cost

                # Save changes to the database
                save_global_state_to_db(user_id, global_state_model)

                # Additional logic to initialize new biomes or plant parts
                if existing_upgrade_model.type == "biome":
                    initialize_new_biome(user_id, existing_upgrade_model.effect)
                print("Upgrade successfully unlocked.")
            else:
                print("Upgrade already unlocked.")
        else:
            print("Not enough genetic markers to unlock this upgrade.")
    else:
        print(f"No upgrade found with id {upgrade_id}")
