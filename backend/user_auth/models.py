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

class PlantTimeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.Integer)
    hour = db.Column(db.Integer)
    is_day = db.Column(db.Boolean)
    season = db.Column(db.String)
    update_counter = db.Column(db.Integer)
    year = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'day': self.day,
            'hour': self.hour,
            'is_day': self.is_day,
            'season': self.season,
            'update_counter': self.update_counter,
            'year': self.year
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            day=data['day'],
            hour=data['hour'],
            is_day=data['is_day'],
            season=data['season'],
            update_counter=data['update_counter'],
            year=data['year']
        )

class GlobalState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    genetic_marker_progress = db.Column(db.Float)
    genetic_marker_threshold = db.Column(db.Integer)
    genetic_markers = db.Column(db.Integer)
    seeds = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'genetic_marker_progress': self.genetic_marker_progress,
            'genetic_marker_threshold': self.genetic_marker_threshold,
            'genetic_markers': self.genetic_markers,
            'seeds': self.seeds
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            genetic_marker_progress=data['genetic_marker_progress'],
            genetic_marker_threshold=data['genetic_marker_threshold'],
            genetic_markers=data['genetic_markers'],
            seeds=data['seeds']
        )