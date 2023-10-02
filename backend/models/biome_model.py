from extensions import db  # Import db from extensions.py

class BiomeModel(db.Model):
    __tablename__ = 'biomes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)  
    ground_water_level = db.Column(db.Float, nullable=False)
    current_weather = db.Column(db.String(50), nullable=False)
    current_pest = db.Column(db.String(50), nullable=True)
    snowpack = db.Column(db.Float, nullable=False)
    resource_modifiers = db.Column(db.JSON, nullable=True) 
    rain_intensity = db.Column(db.Float, nullable=False) 
    snow_intensity = db.Column(db.Float, nullable=False)  

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'capacity': self.capacity,  # New
            'ground_water_level': self.ground_water_level,
            'current_weather': self.current_weather,
            'current_pest': self.current_pest,
            'snowpack': self.snowpack,
            'resource_modifiers': self.resource_modifiers,  # New
            # ... other fields ...
        }
