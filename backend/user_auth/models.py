from ..extensions import db  # Import db from extensions.py
from flask_login import UserMixin
import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_initialized = db.Column(db.Boolean, default=False)  # New field

class UpgradeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    unlocked = db.Column(db.Boolean, default=False)
    effect = db.Column(db.String(50), nullable=True)
    secondary_cost = db.Column(db.Integer, nullable=True)  # Use nullable=True since it's optional
    secondary_resource = db.Column(db.String(50), nullable=True)  # Use nullable=True since it's optional
    cost_modifier = db.Column(db.Float, default=0.0)  # Default to 0 means no change
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    # ... other fields ...
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'cost': self.cost,
            'type': self.type,
            'unlocked': self.unlocked,
            'effect': self.effect,
            'secondary_cost': self.secondary_cost,
            'secondary_resource': self.secondary_resource,
            'cost_modifier': self.cost_modifier,
            'created_at': self.created_at
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
            secondary_cost=data['secondary_cost'],
            secondary_resource=data['secondary_resource'],
            cost_modifier=data['cost_modifier'],
            created_at=datetime.datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
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
        print(f"Data received in from_dict: {data}")  # Debugging line
        instance = cls(
            id=data.get('id', None),  # Using .get() to avoid KeyError
            day=data['day'],
            hour=data['hour'],
            is_day=data['is_day'],
            season=data['season'],
            update_counter=data['update_counter'],
            year=data['year']
        )
        print(f"Instance created from from_dict: {instance}")  # Debugging line
        return instance


class GlobalState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    genetic_marker_progress = db.Column(db.Float)
    genetic_marker_threshold = db.Column(db.Integer)
    genetic_markers = db.Column(db.Integer)
    seeds = db.Column(db.Integer)
    silica = db.Column(db.Integer, default=0)
    tannins = db.Column(db.Integer, default=0)
    calcium = db.Column(db.Integer, default=0)
    fulvic = db.Column(db.Integer, default=0)
    cost_modifier = db.Column(db.Float, default=0.0)  # Default to 0 means no change

    def to_dict(self):
        return {
            'id': self.id,
            'genetic_marker_progress': self.genetic_marker_progress,
            'genetic_marker_threshold': self.genetic_marker_threshold,
            'genetic_markers': self.genetic_markers,
            'seeds': self.seeds,
            'silica': self.silica,
            'tannins': self.tannins,
            'calcium': self.calcium,
            'fulvic': self.fulvic,
            'cost_modifier': self.cost_modifier
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id', None),
            genetic_marker_progress=data['genetic_marker_progress'],
            genetic_marker_threshold=data['genetic_marker_threshold'],
            genetic_markers=data['genetic_markers'],
            seeds=data['seeds'],
            silica=data['silica'],
            tannins=data['tannins'],
            calcium=data['calcium'],
            fulvic=data['fulvic'],
            cost_modifier=data.get('cost_modifier', 0.0)
        )