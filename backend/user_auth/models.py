from extensions import db  # Import db from extensions.py
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    game_state = db.Column(db.String(5000))  # Add this line for game_state, assuming it's a JSON string
