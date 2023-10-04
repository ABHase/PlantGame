"""
Biome Class (biome.py)

    Attributes:
        name: Name of the biome.
        capacity: Maximum number of plants that can be in this biome.
        plants: A list of Plant objects in this biome.
        resource_modifiers: A dictionary containing modifiers for resource absorption rates.

    Methods:
        add_plant(plant): Add a plant to this biome.
        remove_plant(plant): Remove a plant from this biome.
        update(): Update the biome's state (called in the main game loop).
"""
import random
from user_auth.user_auth import save_single_biome_to_db
from biomes.biomes_config import BIOMES
from plants.plant import Plant

class Biome:
    def __init__(self, id, user_id, name, capacity, ground_water_level, current_weather, current_pest, snowpack, resource_modifiers, rain_intensity, snow_intensity):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.capacity = capacity
        self.ground_water_level = ground_water_level
        self.current_weather = current_weather
        self.current_pest = current_pest
        self.snowpack = snowpack
        self.resource_modifiers = resource_modifiers
        self.rain_intensity = rain_intensity
        self.snow_intensity = snow_intensity
        self.weather_conditions = BIOMES[self.name]['weather_conditions']
        self.plants = []  # Initialize an empty list for plants

    @classmethod
    def from_dict(cls, data):
        biome = cls(
            id=data['id'],
            user_id=data['user_id'],
            name=data['name'],
            capacity=data['capacity'],
            ground_water_level=data['ground_water_level'],
            current_weather=data['current_weather'],
            current_pest=data['current_pest'],
            snowpack=data['snowpack'],
            resource_modifiers=data['resource_modifiers'],
            rain_intensity=data['rain_intensity'],
            snow_intensity=data['snow_intensity']
        )
        # If 'plants' key exists in data, convert plant dictionaries to Plant objects
        if 'plants' in data:
            biome.plants = [Plant.from_dict(plant_data) for plant_data in data['plants']]
        return biome

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'capacity': self.capacity,
            'ground_water_level': self.ground_water_level,
            'current_weather': self.current_weather,
            'current_pest': self.current_pest,
            'snowpack': self.snowpack,
            'resource_modifiers': self.resource_modifiers,
            'rain_intensity': self.rain_intensity,
            'snow_intensity': self.snow_intensity,
            'plants': [plant.to_dict() for plant in self.plants]  # Convert each plant to a dictionary
        }


    #Method to decrease ground water level
    def decrease_ground_water_level(self, amount):
        self.ground_water_level = max(0, self.ground_water_level - amount)
        save_single_biome_to_db(self)
    
    #Method to increase ground water level
    def increase_ground_water_level(self, amount):
        self.ground_water_level += amount

    def add_plant(self, plant):
        self.plants.append(plant)

    def remove_plant(self, plant):
        self.plants.remove(plant)

    # Method to check if enough ground water is available
    def has_enough_ground_water(self, amount):
        return self.ground_water_level >= amount
    
    def set_pest_for_day(self, current_season):
        pest_choices = list(BIOMES[self.name].get('pests', {}).keys())
        probabilities = list(BIOMES[self.name].get('pests', {}).values())
        self.current_pest = random.choices(pest_choices, probabilities)[0]

    def set_weather_for_day(self, current_season):
        
        weather_choices = list(self.weather_conditions[current_season].keys())
        probabilities = list(self.weather_conditions[current_season].values())
        self.current_weather = random.choices(weather_choices, probabilities)[0]

    def set_weather_for_hour(self, current_season):
        # You could make this more complex by considering the current weather, time of day, etc.
        weather_choices = list(self.weather_conditions[current_season].keys())
        probabilities = list(self.weather_conditions[current_season].values())
        self.current_weather = random.choices(weather_choices, probabilities)[0]

    def handle_pests(self, current_pest):
        for plant in self.plants:
            plant.handle_pest(current_pest)

    def update(self, is_day, new_day=False, new_hour=False, current_season=None):
        if new_hour and current_season:
            self.set_weather_for_hour(current_season)
        results = []

        if self.current_weather == 'Rainy':
            self.increase_ground_water_level(self.rain_intensity)  # Use the biome-specific rain intensity
        elif self.current_weather == 'Snowy':
            self.snowpack += self.snow_intensity  # Accumulate snowpack

        # Slowly drain water over time
        #self.decrease_ground_water_level(self.ground_water_level * 0.02)  # Example rate

        # Melt snowpack in spring
        if current_season == 'Spring':
            melt_amount = min(self.snowpack, 50)  # You can adjust the melt rate
            self.increase_ground_water_level(melt_amount)
            self.snowpack -= melt_amount

        if new_day and current_season:
            self.set_pest_for_day(current_season)

        if new_hour and self.current_pest is not None:
            self.handle_pests(self.current_pest)

        # Update the plants
        for plant in self.plants:
            can_produce, amount, water_absorbed = plant.update(is_day, self.ground_water_level, self.current_weather)  # Get the additional value
            self.ground_water_level -= water_absorbed  # Update the ground_water_level immediately
            if self.ground_water_level < 0:  # Ensure ground_water_level doesn't go below zero
                self.ground_water_level = 0
            results.append((can_produce, amount))
        
        return results

