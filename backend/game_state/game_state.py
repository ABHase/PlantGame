"""
GameState Class (game_state.py)

    Attributes:
        plants: A list of all Plant objects.
        biomes: A list of all Biome objects.
        upgrades: A list of all Upgrade objects.
        genetic_markers: Total genetic markers.

    Methods:
        add_plant_to_biome(plant, biome): Add a plant to a biome.
        unlock_upgrade(upgrade): Unlock an upgrade.
        purchase_upgrade(upgrade): Purchase an upgrade.
        update(): Update the game state (called in the main game loop).
""" 
from constants import INITIAL_GENETIC_MARKER_THRESHOLD
from plants.plant import Plant
from biomes.biome import Biome
from game_resource import GameResource
from upgrades.upgrade import Upgrade


class GameState:
    def __init__(self, plants, biomes, upgrades, genetic_markers):
        self.plants = plants
        self.biomes = biomes
        self.upgrades = upgrades
        self.genetic_markers = genetic_markers
        self.genetic_marker_progress = 0
        self.genetic_marker_threshold = INITIAL_GENETIC_MARKER_THRESHOLD

    def update(self):
        for biome in self.biomes:
            for plant in biome.plants:
                can_produce, amount = plant.update()
                if can_produce:
                    self.update_genetic_marker_progress(amount)
            biome.update()

        for upgrade in self.upgrades:
            upgrade_conditions = {
                'biome': len(self.biomes) >= 2,
                'plant part': len(self.plants) >= 2,  # You might want to update this condition too
                'genetic marker production rate': len(self.plants) >= 2,  # And this one
                'sugar production rate': len(self.plants) >= 2,  # And this one
                'plant capacity': len(self.biomes) >= 2
            }
            if upgrade.type in upgrade_conditions and upgrade_conditions[upgrade.type]:
                upgrade.unlock()


    def update_genetic_marker_progress(self, amount):
        self.genetic_marker_progress += amount
        if self.genetic_marker_progress >= self.genetic_marker_threshold:
            self.genetic_markers += 1
            self.genetic_marker_progress -= self.genetic_marker_threshold
            self.genetic_marker_threshold += self.genetic_marker_threshold  # Increase the threshold

    def purchase_seed(self, target_biome, sugar_cost, genetic_marker_cost):
        if self.genetic_markers >= genetic_marker_cost:
            for plant in self.plants:
                if plant.resources['sugar'].amount >= sugar_cost:
                    new_plant = plant.produce_seed(target_biome)
                    if new_plant:
                        plant.resources['sugar'].subtract_amount(sugar_cost)
                        self.genetic_markers -= genetic_marker_cost
                        return True  # Seed successfully purchased and planted
        return False  # Failed to purchase seed
    
    def to_dict(self):
        return {
            'biomes': [
                {
                    'name': biome.name,
                    'capacity': biome.capacity,
                    'resource_modifiers': biome.resource_modifiers,
                    'plants': [
                        {
                            'id': plant.id,
                            'maturity_level': plant.maturity_level,
                            'resources': {k: v.amount for k, v in plant.resources.items()},
                            'plant_parts': {k: v.amount for k, v in plant.plant_parts.items()},
                            'is_sugar_production_on': plant.is_sugar_production_on,
                            'is_genetic_marker_production_on': plant.is_genetic_marker_production_on,
                        }
                        for plant in biome.plants
                    ],
                }
                for biome in self.biomes
            ],
            'upgrades': [
                {
                    'name': upgrade.name,
                    'cost': upgrade.cost,
                    'type': upgrade.type,
                    'unlocked': upgrade.unlocked,
                }
                for upgrade in self.upgrades
            ],
            'genetic_markers': self.genetic_markers,
            'genetic_marker_progress': self.genetic_marker_progress,
            'genetic_marker_threshold': self.genetic_marker_threshold,
        }

    @classmethod
    def from_dict(cls, data):
        biomes = []
        for biome_data in data['biomes']:
            plants = []
            for plant_data in biome_data['plants']:
                resources = {k: GameResource(k, v) for k, v in plant_data['resources'].items()}
                plant_parts = {k: GameResource(k, v) for k, v in plant_data['plant_parts'].items()}
                plant = Plant(
                    resources,
                    plant_parts,
                    None,  # Biome will be set later
                    plant_data['maturity_level'],
                    plant_data['is_sugar_production_on'],
                    plant_data['is_genetic_marker_production_on']
                )
                plants.append(plant)
            
            biome = Biome(
                biome_data['name'],
                biome_data['capacity'],
                biome_data['resource_modifiers']
            )
            for plant in plants:
                plant.biome = biome
                biome.add_plant(plant)
            biomes.append(biome)

        upgrades = [Upgrade(upgrade_data['name'], upgrade_data['cost'], upgrade_data['type']) for upgrade_data in data['upgrades']]
        
        return cls(
            [],  # Plants will be populated through biomes
            biomes,
            upgrades,
            data['genetic_markers']
        )

    def __getstate__(self):
        return self.to_dict()

    def __setstate__(self, state):
        self.__dict__.update(GameState.from_dict(state).__dict__)