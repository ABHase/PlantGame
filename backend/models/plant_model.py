from extensions import db  # Import db from extensions.py

class PlantModel(db.Model):
    __tablename__ = 'plants'
    
    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    biome_id = db.Column(db.Integer, db.ForeignKey('biomes.id'), nullable=False)
    maturity_level = db.Column(db.Integer, nullable=False)
    sugar_production_rate = db.Column(db.Float, nullable=False)
    genetic_marker_production_rate = db.Column(db.Float, nullable=False)
    is_sugar_production_on = db.Column(db.Boolean, default=False)
    is_genetic_marker_production_on = db.Column(db.Boolean, default=False)
    
    # Resources as individual columns
    sunlight = db.Column(db.Float, default=0)
    water = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    ladybugs = db.Column(db.Float, default=0)
    
    # Plant parts as individual columns
    roots = db.Column(db.Float, default=2)
    leaves = db.Column(db.Float, default=1)
    vacuoles = db.Column(db.Float, default=1)
    resin = db.Column(db.Float, default=0)
    taproot = db.Column(db.Float, default=0)
    pheromones = db.Column(db.Float, default=0)
    thorns = db.Column(db.Float, default=0)
    # ... add more as needed

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'biome_id': self.biome_id,
            'maturity_level': self.maturity_level,
            'sugar_production_rate': self.sugar_production_rate,
            'genetic_marker_production_rate': self.genetic_marker_production_rate,
            'is_sugar_production_on': self.is_sugar_production_on,
            'is_genetic_marker_production_on': self.is_genetic_marker_production_on,
            'sunlight': self.sunlight,
            'water': self.water,
            'sugar': self.sugar,
            'ladybugs': self.ladybugs,
            'roots': self.roots,
            'leaves': self.leaves,
            'vacuoles': self.vacuoles,
            'resin': self.resin,
            'taproot': self.taproot,
            'pheromones': self.pheromones,
            'thorns': self.thorns
            # ... add more as needed
        }

    def from_dict(self, data):
        for field in ['id', 
                      'user_id', 
                      'biome_id', 
                      'maturity_level', 
                      'sugar_production_rate', 
                      'genetic_marker_production_rate', 
                      'is_sugar_production_on', 
                      'is_genetic_marker_production_on', 
                      'sunlight', 
                      'water', 
                      'sugar', 
                      'ladybugs', 
                      'roots', 
                      'leaves', 
                      'vacuoles', 
                      'resin', 
                      'taproot', 
                      'pheromones', 
                      'thorns']:
            if field in data:
                setattr(self, field, data[field])