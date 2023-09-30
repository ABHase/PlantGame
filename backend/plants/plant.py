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
import math
import uuid
from game_resource import GameResource
from constants import SUGAR_THRESHOLD

class Plant:
    def __init__(self, resources, plant_parts, biome, maturity_level, sugar_production_rate, genetic_marker_production_rate, plant_id=None):
        self.id = plant_id if plant_id else str(uuid.uuid4())
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
        #Print attempted toggle
        print(f"Plant ID: {self.id}")
        print(f"Toggle: Sugar Production")
        self.is_sugar_production_on = not self.is_sugar_production_on

    def toggle_genetic_marker(self):
        self.is_genetic_marker_production_on = not self.is_genetic_marker_production_on

    def purchase_plant_part(self, type, cost):
        #Print attempted purchase
        print(f"Plant ID: {self.id}")
        print(f"Purchase: {type}")
        print(f"Cost: {cost}")
        #If the plant has enough sugar, subtract the cost and add the plant part
        if self.resources['sugar'].amount >= cost:
            self.resources['sugar'].subtract_amount(cost)
            self.plant_parts[type].add_amount(1)
        
    def absorb_resource(self, type, amount):
        self.resources[type].add_amount(amount)

    def produce_sugar(self):
        # Base rate of sugar production
        base_rate = self.sugar_production_rate

        # Modify the rate based on maturity level
        modified_rate = base_rate * (1 + 0.1 * self.maturity_level)

        # Resource consumption rate also depends on maturity
        water_consumption = 10 * (1 + 0.4 * self.maturity_level)
        sunlight_consumption = 10 * (1 + 0.4 * self.maturity_level)

        if self.resources['water'].amount > water_consumption and self.resources['sunlight'].amount > sunlight_consumption:
            self.resources['water'].subtract_amount(water_consumption)
            self.resources['sunlight'].subtract_amount(sunlight_consumption)
            self.resources['sugar'].add_amount(modified_rate)
    
    def produce_genetic_markers(self):
        if self.resources['sugar'].amount <= SUGAR_THRESHOLD:
            return False, 0
        self.resources['sugar'].subtract_amount(SUGAR_THRESHOLD)
        return True, 1

    def grow_plant_part(self, type):
        self.plant_parts[type].add_amount(1)

    def purchase_seed(self, cost):
        print(f"Plant's sugar before purchase: {self.resources['sugar'].amount}")
        if self.resources['sugar'].amount >= cost:
            self.resources['sugar'].subtract_amount(cost)
            return True
        print("Not enough sugar to purchase seed.")
        return False


    def update(self, is_day, ground_water_level):
        can_produce = False
        amount = 0
        water_absorbed = 0  # Initialize water_absorbed

        self.maturity_level = int(math.sqrt(self.plant_parts['roots'].amount + self.plant_parts['leaves'].amount))

        if self.is_sugar_production_on:
            self.produce_sugar()

        # For each root absorb 1 water per second
        for root in range(self.plant_parts['roots'].amount):
            if ground_water_level > 0:  # Check if there's enough water in the ground
                self.resources['water'].add_amount(1)
                water_absorbed += 1  # Increment water_absorbed
                ground_water_level -= 1  # Decrement ground_water_level

        # For each leaf absorb 1 sunlight per second
        if is_day:
            for leaf in range(self.plant_parts['leaves'].amount):
                self.resources['sunlight'].add_amount(1)

        if self.plant_parts['roots'].amount > 10 and self.plant_parts['leaves'].amount > 10:
            self.maturity_level = 1

        if self.is_genetic_marker_production_on:
            can_produce, amount = self.produce_genetic_markers()

        return can_produce, amount, water_absorbed  # Return three values
