from app import db  # Replace 'your_app' with the name of your main app package
from .models import User  # Replace 'your_app' with the name of your main app package
from flask import json
from datetime import datetime

def log_with_timestamp(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")


def fetch_game_state_from_db(user_id):
    user = User.query.get(user_id)
    if user and user.game_state:
        #log_with_timestamp(f"Fetching game state for user_id: {user_id}")
        #log_with_timestamp("Game state loaded from database {}.".format(user.game_state))
        return json.loads(user.game_state)
    #log_with_timestamp(f"No game state found for user_id: {user_id}")
    return None

def save_game_state_to_db(user_id, game_state):
    user = User.query.get(user_id)
    if user:
        #log_with_timestamp(f"Saving game state for user_id: {user_id}")
        #log_with_timestamp("Game state before saving: {}".format(game_state))
        user.game_state = json.dumps(game_state)
        db.session.commit()
        #log_with_timestamp("Game state after saving: {}".format(game_state))
