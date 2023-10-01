from extensions import db  # Import db from extensions.py
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    game_state = db.Column(db.String(5000))  # Add this line for game_state, assuming it's a JSON string

class UpgradeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    unlocked = db.Column(db.Boolean, default=False)
    effect = db.Column(db.String(50), nullable=True)
    # ... other fields ...
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'cost': self.cost,
            'type': self.type,
            'unlocked': self.unlocked,
            'effect': self.effect
            # ... other fields ...
        }
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            name=data['name'],
            type=data['type'],
            effect=data['effect'],
            unlocked=data['unlocked'],
            # ... any other fields ...
        )
