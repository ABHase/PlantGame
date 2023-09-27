"""
Plant Class (plant.py)

Attributes:
    resources: A dictionary containing the resources (sunlight, water, sugar).
    plant_parts: A dictionary containing the plant parts (roots, leaves).
    biome: Reference to the biome it belongs to.
    maturity_level: An integer or string indicating the maturity level.
    sugar_production_rate: A float indicating the rate of sugar production.
    genetic_marker_production_rate: A float indicating the rate of genetic marker production.

Methods:

    absorb_resource(type, amount): Absorb a resource of a given type and amount.
    produce_sugar(): Produce sugar based on the current state.
    grow_plant_part(type): Grow a plant part (root or leaf).
    produce_seed(): Produce a new seed/plant.
    update(): Update the plant's state (called in the main game loop).

"""
import copy
import uuid
from game_resource import GameResource
from constants import SUGAR_THRESHOLD

class Plant:
    def __init__(self, resources, plant_parts, biome, maturity_level, sugar_production_rate, genetic_marker_production_rate):
        self.id = str(uuid.uuid4())
        self.resources = resources
        self.plant_parts = plant_parts
        self.biome = biome
        self.maturity_level = maturity_level
        self.sugar_production_rate = sugar_production_rate
        self.genetic_marker_production_rate = genetic_marker_production_rate
        self.is_sugar_production_on = False
        self.is_genetic_marker_production_on = False

    #Method for plant to die and remove itself from the biome
    def die(self):
        self.biome.remove_plant(self)

    def toggle_sugar_production(self):
        self.is_sugar_production_on = not self.is_sugar_production_on

    def toggle_genetic_marker_production(self):
        self.is_genetic_marker_production_on = not self.is_genetic_marker_production_on

    def purchase_plant_part(self, type, cost):
        if self.resources['sugar'].amount >= cost:
            self.resources['sugar'].subtract_amount(cost)
            self.plant_parts[type].add_amount(1)
        
    def absorb_resource(self, type, amount):
        self.resources[type].add_amount(amount)

    def produce_sugar(self):
        #If water and sunlight are both over 30, subtract 10 from each and produce sugar
        if self.resources['water'].amount > 30 and self.resources['sunlight'].amount > 30:
            self.resources['water'].subtract_amount(10)
            self.resources['sunlight'].subtract_amount(10)
            self.resources['sugar'].add_amount(self.sugar_production_rate)
    
    def produce_genetic_markers(self):
        if self.resources['sugar'].amount > SUGAR_THRESHOLD:
            self.resources['sugar'].subtract_amount(SUGAR_THRESHOLD)
            return True, 1  # Can produce, and the amount to produce
        return False, 0  # Cannot produce


    def grow_plant_part(self, type):
        self.plant_parts[type].add_amount(1)

    def produce_seed(self, target_biome):
        if len(target_biome.plants) < target_biome.capacity:
            initial_resources = {
                'sunlight': GameResource('sunlight', 0),
                'water': GameResource('water', 0),
                'sugar': GameResource('sugar', 0),
            }
            initial_plant_parts = {'roots': GameResource('roots', 0), 'leaves': GameResource('leaves', 0)}
            new_plant = Plant(initial_resources, initial_plant_parts, target_biome, 0, self.sugar_production_rate, self.genetic_marker_production_rate)
            target_biome.add_plant(new_plant)
            return new_plant
        else:
            return None  # Return None if the biome is full


    def update(self):
        can_produce = False
        amount = 0

        if self.is_sugar_production_on:
            self.produce_sugar()

        # For each root absorb 1 water per second
        for root in range(self.plant_parts['roots'].amount):
            self.resources['water'].add_amount(1/60.0)

        # For each leaf absorb 1 sunlight per second
        for leaf in range(self.plant_parts['leaves'].amount):
            self.resources['sunlight'].add_amount(1/60.0)
            #print self id
            print(f"Plant ID: {self.id}")
            print(f"Sunlight: {self.resources['sunlight'].amount}")

        if self.plant_parts['roots'].amount > 10 and self.plant_parts['leaves'].amount > 10:
            self.maturity_level = 1

        if self.is_genetic_marker_production_on:
            can_produce, amount = self.produce_genetic_markers()

        return can_produce, amount  # Always return a tuple

