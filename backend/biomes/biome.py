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
    def __init__(self, name, capacity, resource_modifiers):
        self.name = name
        self.capacity = capacity
        self.plants = []
        self.resource_modifiers = resource_modifiers


    def add_plant(self, plant):
        self.plants.append(plant)

    def remove_plant(self, plant):
        self.plants.remove(plant)

    def update(self):
        for plant in self.plants:
            plant.update()