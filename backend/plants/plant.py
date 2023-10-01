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
    def __init__(self, resources, plant_parts, biome, maturity_level, sugar_production_rate, genetic_marker_production_rate, plant_id=None,is_sugar_production_on=False,is_genetic_marker_production_on=False):

        self.id = plant_id if plant_id else str(uuid.uuid4())
        self.resources = resources
        self.plant_parts = plant_parts
        self.biome = biome
        self.maturity_level = maturity_level
        self.sugar_production_rate = sugar_production_rate
        self.genetic_marker_production_rate = genetic_marker_production_rate
        self.is_sugar_production_on = is_sugar_production_on
        self.is_genetic_marker_production_on = is_genetic_marker_production_on

    #Method for plant to die and remove itself from the biome
    def die(self):
        self.biome.remove_plant(self)

    def toggle_sugar_production(self):
        self.is_sugar_production_on = not self.is_sugar_production_on

    def toggle_genetic_marker(self):
        self.is_genetic_marker_production_on = not self.is_genetic_marker_production_on

    def purchase_plant_part(self, type, cost):
        if self.resources['sugar'].amount >= cost:
            if type == 'resin':
                if self.plant_parts['resin'].amount >= self.plant_parts['leaves'].amount:
                    print("Cannot purchase more resin than the number of leaves.")
                    return
            self.resources['sugar'].subtract_amount(cost)
            self.plant_parts[type].add_amount(1)
        
    def absorb_resource(self, type, amount):
        if type == 'water':
            max_water_capacity = self.plant_parts['vacuoles'].amount * 100  # Assuming each vacuole can hold 100 units of water
            if self.resources['water'].amount + amount > max_water_capacity:
                return
        self.resources[type].add_amount(amount)

    def produce_sugar(self):
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
    
    def update_maturity_level(self):
        self.maturity_level = int(math.sqrt(self.plant_parts['roots'].amount + self.plant_parts['leaves'].amount))

    def absorb_water(self, ground_water_level):
        water_absorbed = 0
        for root in range(self.plant_parts['roots'].amount):
            if ground_water_level > 0 and self.resources['water'].amount < self.plant_parts['vacuoles'].amount * 100:
                self.resources['water'].add_amount(1)
                water_absorbed += 1
                ground_water_level -= 1
        return water_absorbed, ground_water_level

    def absorb_sunlight(self, is_day, current_weather):
        water_consumption = 1  # Default water consumption
        for leaf in range(self.plant_parts['leaves'].amount):
            if self.plant_parts['resin'].amount > leaf:
                water_consumption = 0  # No water consumption if there's resin
            if is_day and current_weather == 'Sunny':
                self.resources['water'].amount = max(0, self.resources['water'].amount - water_consumption)
                self.resources['sunlight'].add_amount(1)
            else:
                self.resources['sunlight'].amount = max(0, self.resources['sunlight'].amount - 2)
                self.resources['water'].amount = max(0, self.resources['water'].amount - water_consumption)

    def update(self, is_day, ground_water_level, current_weather):
        self.update_maturity_level()

        if self.is_sugar_production_on:
            self.produce_sugar()

        water_absorbed, ground_water_level = self.absorb_water(ground_water_level)
        self.absorb_sunlight(is_day, current_weather)

        can_produce, amount = False, 0
        if self.is_genetic_marker_production_on:
            can_produce, amount = self.produce_genetic_markers()

        return can_produce, amount, water_absorbed
