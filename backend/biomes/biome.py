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
from biomes.biomes_config import BIOMES

class Biome:
    def __init__(self, name, ground_water_level, current_weather, snowpack=0):
        self.name = name
        self.capacity = BIOMES[name]['capacity']
        self.resource_modifiers = BIOMES[name]['resource_modifiers']
        self.weather_conditions = BIOMES[name]['weather_conditions']
        self.rain_intensity = BIOMES[name]['rain_intensity']  # New field
        self.snow_intensity = BIOMES[name]['snow_intensity']
        self.plants = []
        self.ground_water_level = ground_water_level  # Set to passed-in value
        self.current_weather = current_weather  # Set to passed-in value
        self.snowpack = snowpack  # Set to passed-in value


    #Method to decrease ground water level
    def decrease_ground_water_level(self, amount):
        self.ground_water_level = max(0, self.ground_water_level - amount)
    
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

    def set_weather_for_day(self, current_season):
        
        weather_choices = list(self.weather_conditions[current_season].keys())
        probabilities = list(self.weather_conditions[current_season].values())
        self.current_weather = random.choices(weather_choices, probabilities)[0]


    def update(self, is_day, new_day=False, current_season=None):
        if new_day and current_season:
            self.set_weather_for_day(current_season)
        results = []

        if self.current_weather == 'Rainy':
            self.increase_ground_water_level(self.rain_intensity)  # Use the biome-specific rain intensity
        elif self.current_weather == 'Snowy':
            self.snowpack += self.snow_intensity  # Accumulate snowpack

        # Slowly drain water over time
        self.decrease_ground_water_level(self.ground_water_level * 0.1)  # Example rate

        # Melt snowpack in spring
        if current_season == 'Spring':
            melt_amount = min(self.snowpack, 50)  # You can adjust the melt rate
            self.increase_ground_water_level(melt_amount)
            self.snowpack -= melt_amount

        # Update the plants
        for plant in self.plants:
            can_produce, amount, water_absorbed = plant.update(is_day, self.ground_water_level)  # Get the additional value
            self.ground_water_level -= water_absorbed  # Update the ground_water_level immediately
            if self.ground_water_level < 0:  # Ensure ground_water_level doesn't go below zero
                self.ground_water_level = 0
            results.append((can_produce, amount))
        
        return results

