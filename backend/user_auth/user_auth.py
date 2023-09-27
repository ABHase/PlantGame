from app import db  # Replace 'your_app' with the name of your main app package
from .models import User  # Replace 'your_app' with the name of your main app package
from flask import json

def fetch_game_state_from_db(user_id):
    user = User.query.get(user_id)
    if user and user.game_state:
        return json.loads(user.game_state)
    return None

def save_game_state_to_db(user_id, game_state):
    user = User.query.get(user_id)
    if user:
        user.game_state = json.dumps(game_state)
        db.session.commit()