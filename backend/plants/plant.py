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
from user_auth.user_auth import save_single_plant_to_db
from game_resource import GameResource
from constants import SUGAR_THRESHOLD
from plants.plant_parts_config import PLANT_PARTS_CONFIG
from plants.part_cost_config import PARTS_COST_CONFIG


class Plant:
    def __init__(self, 
                 id, 
                 user_id, 
                 biome_id, 
                 maturity_level, 
                 sugar_production_rate, 
                 genetic_marker_production_rate, 
                 is_sugar_production_on, 
                 is_genetic_marker_production_on,
                 sunlight, 
                 water, 
                 sugar, 
                 ladybugs, 
                 roots, 
                 leaves, 
                 vacuoles, 
                 resin, 
                 taproot, 
                 pheromones, 
                 thorns):
        
        self.id = id
        self.user_id = user_id
        self.biome_id = biome_id
        self.maturity_level = maturity_level
        self.sugar_production_rate = sugar_production_rate
        self.genetic_marker_production_rate = genetic_marker_production_rate
        self.is_sugar_production_on = is_sugar_production_on
        self.is_genetic_marker_production_on = is_genetic_marker_production_on
        
        # Resources
        self.sunlight = sunlight
        self.water = water
        self.sugar = sugar
        self.ladybugs = ladybugs
        
        # Plant parts
        self.roots = roots
        self.leaves = leaves
        self.vacuoles = vacuoles
        self.resin = resin
        self.taproot = taproot
        self.pheromones = pheromones
        self.thorns = thorns

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            biome_id=data['biome_id'],
            maturity_level=data['maturity_level'],
            sugar_production_rate=data['sugar_production_rate'],
            genetic_marker_production_rate=data['genetic_marker_production_rate'],
            is_sugar_production_on=data['is_sugar_production_on'],
            is_genetic_marker_production_on=data['is_genetic_marker_production_on'],
            sunlight=data['sunlight'],
            water=data['water'],
            sugar=data['sugar'],
            ladybugs=data['ladybugs'],
            roots=data['roots'],
            leaves=data['leaves'],
            vacuoles=data['vacuoles'],
            resin=data['resin'],
            taproot=data['taproot'],
            pheromones=data['pheromones'],
            thorns=data['thorns']
        )

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
        }

    def toggle_sugar_production(self):
        self.is_sugar_production_on = not self.is_sugar_production_on
        save_single_plant_to_db(self)

    def toggle_genetic_marker(self):
        self.is_genetic_marker_production_on = not self.is_genetic_marker_production_on
        save_single_plant_to_db(self)

    def purchase_plant_part(self, type):
        cost = PARTS_COST_CONFIG.get(type, 0)  # Get the cost from the config, default to 0 if type is not found

        if cost == 0:
            print(f"Invalid plant part type: {type}")
            return

        if type == 'resin' and self.resin >= self.leaves:
            print("Cannot purchase more resin than the number of leaves.")
            return

        if self.sugar >= cost:
            setattr(self, type, getattr(self, type) + 1)
            self.sugar -= cost
        else:
            print(f"Not enough sugar to purchase {type}.")
        save_single_plant_to_db(self)

    def absorb_resource(self, type, amount):
        if type == 'water':
            max_water_capacity = self.vacuoles * 100
            if self.water + amount > max_water_capacity:
                return
        setattr(self, type, getattr(self, type) + amount)
        save_single_plant_to_db(self)

    def produce_sugar(self):
        base_rate = self.sugar_production_rate
        modified_rate = base_rate * (1 + 0.1 * self.maturity_level)
        water_consumption = 10 * (1 + 0.4 * self.maturity_level)
        sunlight_consumption = 10 * (1 + 0.4 * self.maturity_level)

        if self.water > water_consumption and self.sunlight > sunlight_consumption:
            self.water -= water_consumption
            self.sunlight -= sunlight_consumption
            self.sugar += modified_rate

    def produce_genetic_markers(self):
        if self.sugar <= SUGAR_THRESHOLD:
            return False, 0
        self.sugar -= SUGAR_THRESHOLD
        return True, 1

    def grow_plant_part(self, type):
        setattr(self, type, getattr(self, type) + 1)

    def purchase_seed(self, cost):
        if self.sugar >= cost:
            self.sugar -= cost
            return True
        return False

    def update_maturity_level(self):
        self.maturity_level = int(math.sqrt(self.roots + self.leaves))

    def absorb_water(self, ground_water_level):
        water_absorbed = 0
        for _ in range(int(self.roots)):
            if ground_water_level > 0 and self.water < self.vacuoles * 100:
                self.water += 1
                water_absorbed += 1
                ground_water_level -= 1
        return water_absorbed, ground_water_level

    def absorb_sunlight(self, is_day, current_weather):
        water_consumption = 1
        for _ in range(int(self.leaves)):
            if self.resin > 0:
                water_consumption = 0
            if is_day and current_weather == 'Sunny':
                self.water = max(0, self.water - water_consumption)
                self.sunlight += 1

    def attract_ladybugs(self):
        if self.pheromones > 0:
            self.ladybugs += 1
            self.pheromones -= 1

    def handle_pest(self, current_pest):
        if current_pest == 'Aphids':
            if self.ladybugs > 0:
                self.ladybugs -= 1
            else:
                self.sugar = max(0, self.sugar - 10)
        elif current_pest == 'Deer':
            if self.thorns > 0:
                self.thorns -= 1
            else:
                self.leaves = max(0, self.leaves - 1)

    def update(self, is_day, ground_water_level, current_weather):
        print(f"Plant {self.id} updating...")
        self.update_maturity_level()
        self.attract_ladybugs()

        if self.is_sugar_production_on:
            self.produce_sugar()

        water_absorbed, ground_water_level = self.absorb_water(ground_water_level)
        self.absorb_sunlight(is_day, current_weather)

        can_produce, amount = False, 0
        if self.is_genetic_marker_production_on:
            can_produce, amount = self.produce_genetic_markers()

        return can_produce, amount, water_absorbed
