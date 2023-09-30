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
class Biome:
    def __init__(self, name, capacity, resource_modifiers, ground_water_level=100):
        self.name = name
        self.capacity = capacity
        self.plants = []
        self.resource_modifiers = resource_modifiers
        self.ground_water_level = ground_water_level

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

    def update(self, is_day):
        results = []
        for plant in self.plants:
            can_produce, amount, water_absorbed = plant.update(is_day, self.ground_water_level)  # Get the additional value
            self.ground_water_level -= water_absorbed  # Update the ground_water_level immediately
            if self.ground_water_level < 0:  # Ensure ground_water_level doesn't go below zero
                self.ground_water_level = 0
            results.append((can_produce, amount))
        
        return results

