from user_auth.models import UpgradeModel
from user_auth.user_auth import fetch_upgrade_by_index

def handle_unlock_upgrade(action, game_state):
    user_id = action["user_id"]
    index = action["index"]
    cost = action["cost"]
    upgrade = fetch_upgrade_by_index(user_id, index)

    print(f"Cost in handle_unlock_upgrade: {cost}")

    # Check if the user has enough genetic markers
    if game_state.genetic_markers >= cost:
        if not upgrade.unlocked:
            upgrade.unlocked = True  # Unlock the upgrade
            game_state.handle_unlock_upgrade(UpgradeModel.from_dict(upgrade.to_dict()), cost)
    else:
        print("Not enough genetic markers to unlock this upgrade.")
