from user_auth.models import UpgradeModel
from user_auth.user_auth import fetch_upgrade_by_index

def handle_unlock_upgrade(action, game_state):
    user_id = action["user_id"]  # Retrieve user_id from the action
    index = action["index"]
    upgrade = fetch_upgrade_by_index(user_id, index)  # Pass both user_id and index
    if not upgrade.unlocked:
        upgrade.unlocked = True
        game_state.emit("unlock_upgrade", UpgradeModel.from_dict(upgrade.to_dict()))
